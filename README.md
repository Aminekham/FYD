# Find Your Job

**Find Your Job** is an AI-powered platform designed to revolutionize the job-seeking experience. It leverages cutting-edge machine learning models such as **YOLOv8** for resume segmentation, **ESRGAN** for image enhancement, **Alpaca** for text correction, and **SBERT** for precise resume-job matching.
<br />

## Features

|--------------------------------------------|-------------------------------------------|------------------------------------------|
| ✓ **YOLOv8 Resume Segmentation**          |
| ✓ **ESRGAN Image Enhancement**             | 
| ✓ **Alpaca Text Correction**               |
| ✓ **SBERT Resume-Job Matching**            |
| ✓ **Docker & SQLite**                      | 

!Find Your Job - AI-driven platform

<br />

## ✅ Start in Docker

**Step 1** - Clone the repository:

```bash
$ git clone https://github.com/Aminekham/FYD.git
$ cd FYD

Step 2 - Build the Docker image:

$ docker build -t find-your-job .

Step 3 - Run the Docker container:

$ docker run -p 8000:8000 find-your-job

Step 4 - Access the application:

Open your web browser and go to http://localhost:8000.

<br />

📂 Project Structure
The project is organized as follows:

FindYourJob/
├── apps/
│   ├── authentication/
│   ├── home/
│   ├── resume_processing/
│   ├── static/
│   ├── templates/
│   ├── init.py
│   ├── config.py
├── csvtodb/
│   ├── csvtodb.py
│   ├── showdb.py
├── instance/
├── media/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── visualization/
├── Dockerfile
└── run.py
├── README.md
└── requirements.txt

data/: Contains raw and processed data.
models/: Contains pre-trained models and scripts for training new models.
notebooks/: Jupyter notebooks for exploratory data analysis and prototyping.
src/: Source code for data processing, feature engineering, model training, and visualization.
tests/: Unit tests for the project.
Dockerfile: Instructions to build the Docker image.
requirements.txt: List of dependencies required to run the project.

🛠️ Technologies Used
Python: The main programming language used for development.
YOLOv8: Used for resume segmentation.
ESRGAN: Used for image enhancement.
Alpaca: Used for text correction.
SBERT: Used for resume-job matching.
Docker: Used for containerization.
SQLite: Used as the database.

🚀 Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Make sure you have requirements.txt installed + Ultralytics + transformers + PymuPDF.

Installation
Clone the repo
git clone https://github.com/Aminekham/FYD.git
cd FYD

Run the python API
python run.py

Access the application
Open your web browser and go to http://localhost:500.


🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

Open only for web contributions
Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request

📧 Contact
Mohamed Amine Khammassi - lkham0508@gmail.com

Project Link: https://github.com/Aminekham/FYD

🙏 Acknowledgements
YOLOv8
ESRGAN
Alpaca
SBERT
Docker
SQLite
