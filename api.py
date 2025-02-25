import base64
import requests
from fastapi import UploadFile
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF
import os

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"
DOCUMENT_TYPES = ["Land Records", "Caste Certificates", "Property Registrations"]

# Encode uploaded file
async def encode_file(uploaded_file: UploadFile):
    """Encode uploaded file to base64."""
    file_bytes = await uploaded_file.read()
    
    if uploaded_file.content_type == "application/pdf":
        pdf = fitz.open(stream=BytesIO(file_bytes))
        page = pdf[0]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    elif uploaded_file.content_type.startswith('image/'):
        img = Image.open(BytesIO(file_bytes))
    else:
        return None

    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

# Query Gemini API
def query_gemini(prompt, image_b64=None):
    """Send a request to the Gemini API and return the response."""
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    parts = [{"text": prompt}]
    
    if image_b64:
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})
    
    response = requests.post(url, json={"contents": [{"parts": parts}]}, headers={"Content-Type": "application/json"}, timeout=30)
    if response.status_code != 200:
        return {"error": f"API request failed: {response.status_code}"}
    
    data = response.json()
    return data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response')

# Process uploaded document
async def process_uploaded_file(uploaded_file: UploadFile):
    """Process the uploaded file and return analysis."""
    image_b64 = await encode_file(uploaded_file)
    if not image_b64:
        return {"error": "Unsupported file format"}

    classify_prompt = f"Classify this document into: {', '.join(DOCUMENT_TYPES)}"
    doc_type = query_gemini(classify_prompt, image_b64)

    extract_prompt = "Extract and organize important details (Names, Dates, ID numbers, Locations, Key terms)."
    details = query_gemini(extract_prompt, image_b64)

    verify_prompt = "Analyze for tampering or forgery signs."
    verification = query_gemini(verify_prompt, image_b64)

    return {
        "type": doc_type or "Unclassified",
        "details": details or "No details extracted",
        "verification": verification or "Verification failed"
    }
