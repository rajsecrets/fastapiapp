from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import requests
import fitz  # PyMuPDF for PDF processing
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# Request payload model
class DocumentRequest(BaseModel):
    text: str

@app.post("/process_document/")
async def process_document(file: UploadFile = File(...)):
    try:
        # Check file type
        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(file)
        elif file.content_type.startswith("image/"):
            text = extract_text_from_image(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Send extracted text to Gemini API
        summary = query_gemini(text)

        return {"extracted_text": text, "gemini_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text("text")
    return text.strip()

# Function to extract text from image (Placeholder: Replace with OCR if needed)
def extract_text_from_image(file):
    image = Image.open(io.BytesIO(file.file.read()))
    return "Image text extraction is not implemented yet."

# Function to query Gemini API
def query_gemini(text):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing API Key")

    url = "https://api.gemini.com/v1/analyze"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    data = {"text": text}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json().get("summary", "No summary generated")

