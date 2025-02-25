from fastapi import FastAPI, UploadFile, File
from api import process_uploaded_file

app = FastAPI(title="DocVerify AI API")

@app.get("/")
def root():
    return {"message": "Welcome to DocVerify AI API"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    """
    API endpoint to upload and process a document.
    Expects a file in multipart/form-data.
    """
    result = await process_uploaded_file(file)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
