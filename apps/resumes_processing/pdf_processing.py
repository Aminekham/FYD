from ultralytics import YOLO
import fitz
from PIL import Image
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
labels_list = ['Certifications', 'Community', 'Contact', 'Education', 'Experience', 'Interests', 'Languages', 'Name', 'Profil', 'Projects', 'skills']
matcher = Matcher(nlp.vocab)
model = YOLO("/home/amine/resume_rec_system/web_version_final/flask-atlantis-dark/apps/resumes_processing/best(3).pt")

def clean_text(text):
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()'-\"é@_àçàâäéèêëîïôöùûüÿç ")
    cleaned_text = ''.join(char for char in text if char in allowed_chars)
    return cleaned_text

def process_pdf(pdf_binary_data):
    pdf_document = fitz.open(stream=pdf_binary_data, filetype="pdf")
    processed_results = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        zoom = 1
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        results = model(img)[0]
        for i, result in enumerate(results.boxes.xyxy.tolist()):
            x1, y1, x2, y2 = result
            label = int(results.boxes.cls[i])
            rect = fitz.Rect(x1, y1, x2, y2)
            text = page.get_textbox(rect)
            text = clean_text(text)
            processed_results.append((labels_list[label], text))
    pdf_document.close()
    return processed_results
