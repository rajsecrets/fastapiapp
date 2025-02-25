from fastapi import FastAPI, UploadFile, File
from api import process_uploaded_file

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to DocVerify AI API"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    """API to upload and process a document."""
    result = await process_uploaded_file(file)
    return result
