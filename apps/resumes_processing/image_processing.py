from pdf2image import convert_from_bytes
import pytesseract
from ultralytics import YOLO
from shapely.geometry import box
import cv2
import numpy as np
import re

model = YOLO("/home/amine/resume_rec_system/web_version_final/flask-atlantis-dark/apps/resumes_processing/best(3).pt")

labels_list = [
    'Achievement', 'Certifications', 'Community', 'Contact', 
    'Education', 'Experience', 'Interests', 'Languages', 
    'Name', 'Profil', 'Projects', 'image', 'resume', 'skills'
]
def pdf_to_image(pdf_binary_data):
    images = convert_from_bytes(pdf_binary_data)
    image_arrays = []
    
    for image in images:
        image_array = np.array(image)
        if image_array.shape[2] == 4:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
        else:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        image_arrays.append(image_array)
    return image_arrays

def overlap_ratio(box1, box2):
    rect1 = box(*box1)
    rect2 = box(*box2)
    intersection = rect1.intersection(rect2)
    area_intersection = intersection.area
    area_box1 = rect1.area
    area_box2 = rect2.area
    overlap_ratio1 = area_intersection / area_box1
    overlap_ratio2 = area_intersection / area_box2
    return max(overlap_ratio1, overlap_ratio2)

def segment_image(image):
    results = model(image)[0]
    return results

def process_output(results):
    classes = list(int(result) for result in results.boxes.cls.tolist())
    boxes = list(result for result in results.boxes.xyxy.tolist())
    return classes, boxes

def filter_results(results, threshold=0.1):
    processed_results = []
    seen_regions = set()
    for result in sorted(results.boxes.data.tolist(), key=lambda x: x[4], reverse=True):
        x1, y1, x2, y2, score, _ = result
        region_key = (x1, y1, x2, y2)
        if all(overlap_ratio(region_key, seen_region) < threshold for seen_region in seen_regions) and score > threshold:
            seen_regions.add(region_key)
            processed_results.append(result)
    return processed_results

def clean_text(text):
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()'-\" ")
    cleaned_text = ''.join(char for char in text if char in allowed_chars or char == '<br>')  # Allow <br> tag
    return cleaned_text

def extract_text(results, image, threshold=0.1):
    filtered_results = filter_results(results, threshold)
    processed_results = []
    for result in filtered_results:
        x1, y1, x2, y2, _, class_id = result
        cropped_region = image[int(y1):int(y2), int(x1):int(x2)]
        noise_canceling = cv2.GaussianBlur(cropped_region, (5, 5), 1, 1)
        text = pytesseract.image_to_string(noise_canceling)
        cleaned_text = clean_text(text)
        processed_results.append((labels_list[int(class_id)], cleaned_text))
    return processed_results
