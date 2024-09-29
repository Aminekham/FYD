import os
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit
from flask import request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from apps.config import config_dict
from apps import create_app, db
from flask_login import current_user
from flask import Flask, render_template, make_response
from apps.config import Config
from apps.authentication.models import Resumes
from datetime import datetime
from apps.resumes_processing.image_processing import pdf_to_image, segment_image, process_output, extract_text
import numpy as np
import cv2
import mimetypes
from apps.resumes_processing.pdf_processing import process_pdf
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import requests

app = Flask(__name__)
app.config.from_object(Config)
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
get_config_mode = 'Debug' if DEBUG else 'Production'
BERT_API_URL = 'http://localhost:3000/bert-match'
try:
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG))
    app.logger.info('Page Compression = ' + ('FALSE' if DEBUG else 'TRUE'))
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download_resume/<int:resume_id>', methods=['GET'])
def download_resume(resume_id):
    resume = Resumes.query.get(resume_id)
    if resume:
        response = make_response(resume.resume_data)
        response.headers.set('Content-Type', resume.content_type)
        response.headers.set('Content-Disposition', f'attachment; filename={resume.filename}')
        return response
    return "Resume not found", 404

@app.template_filter('nl2br')
def nl2br(value):
    return value.replace('\n', '<br>') if value else ''

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('home_blueprint.index'))
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home_blueprint.index'))
    if file:
        resume_data = file.read()
        content_type = file.content_type
        filename = file.filename
        new_resume = Resumes(
            user_id=current_user.id,
            resume_data=resume_data,
            filename=filename,
            content_type=content_type
        )
        db.session.add(new_resume)
        db.session.commit()
        flash('Resume uploaded successfully', 'success')
        return redirect(url_for('process_resume'))

@app.route('/change_resume', methods=['POST'])
def change_resume():
    if 'resume' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['resume']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('home_blueprint.index'))
    print(current_user.id)
    if file:
        resume_data = file.read()
        content_type = file.content_type
        filename = file.filename
        existing_resumes = Resumes.query.filter_by(user_id=current_user.id).all()
        if existing_resumes:
            recent_resume = existing_resumes[-1]
            recent_resume.resume_data = resume_data
            recent_resume.filename = filename
            recent_resume.content_type = content_type
            recent_resume.uploaded_at = datetime.utcnow()
            db.session.commit()
        else:
            new_resume = Resumes(
                user_id=current_user.id,
                resume_data=resume_data,
                filename=filename,
                content_type=content_type
            )
            db.session.add(new_resume)
            db.session.commit()
        flash('Resume changed successfully', 'success')
        return redirect(url_for('process_resume'))
@app.route('/resumes', methods=['GET'])
def show_resumes():
    if not current_user.is_authenticated:
        flash('Please log in to view your resumes.', 'error')
        return redirect(url_for('authentication_blueprint.login'))
    resumes = Resumes.query.filter_by(user_id=current_user.id).all()
    return render_template('resumes/show.html', resumes=resumes)

@app.route('/process_resume', methods=["GET"])
def process_resume():
    if not current_user.is_authenticated:
        flash('Please log in to view your resumes.', 'error')
        return redirect(url_for('authentication_blueprint.login'))
    resumes = Resumes.query.filter_by(user_id=current_user.id).all()
    if not resumes:
        flash('No resumes found.', 'error')
        return redirect(url_for('home_blueprint.index'))
    resume = resumes[-1]
    resume_data = resume.resume_data
    file_type, _ = mimetypes.guess_type(resume.filename)
    if file_type == 'application/pdf':
        all_text = process_pdf(resume_data)
    elif file_type.startswith('image/'):
        image = cv2.imdecode(np.frombuffer(resume_data, np.uint8), cv2.IMREAD_COLOR)
        results = segment_image(image)
        classes, boxes = process_output(results)
        all_text = extract_text(results, image)
    else:
        flash('Unsupported file format.', 'error')
        return redirect(url_for('home_blueprint.index'))
    flash('Resume processed successfully.', 'success')
    return render_template('home/index.html', processed_text=all_text)

@app.route('/matching_db', methods=["GET"])
def matching_db():
    resumes = Resumes.query.filter_by(user_id=current_user.id).all()
    if not resumes:
        flash('No resumes found.', 'error')
        return redirect(url_for('home_blueprint.index'))
    resume = resumes[-1]
    print("lsjdfksljf")
    print(resume)
    resume_text_list = [text for _, text in process_pdf(resume.resume_data)]
    resume_text = " ".join(resume_text_list)
    print(resume_text)
    print("Resume Text: ", resume_text)
    conn = sqlite3.connect('jobs_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT processed_job_title, processed_job_description FROM jobs')
    jobs = cursor.fetchall()
    if not jobs:
        flash('No jobs found in the database.', 'error')
        return redirect(url_for('home_blueprint.index'))
    data = [resume_text] + [job[1] for job in jobs]
    try:
        response = requests.post(BERT_API_URL, json={'data': data})
        response.raise_for_status()
        embeddings = response.json().get('embeddings')
        resume_embedding = embeddings[0]
        job_embeddings = embeddings[1:]
        similarity_matrix = cosine_similarity([resume_embedding], job_embeddings)
        most_similar_job_idx = similarity_matrix.argsort()[0][-20:][::-1]
        top_matches = [(jobs[idx][0], jobs[idx][1]) for idx in most_similar_job_idx]
        conn.close()
        return render_template('home/matching.html', top_matches=top_matches)
    except requests.exceptions.RequestException as e:
        flash(f"Error connecting to BERT API: {str(e)}", 'error')
        return redirect(url_for('home_blueprint.index'))

if __name__ == "__main__":
    app.run()
