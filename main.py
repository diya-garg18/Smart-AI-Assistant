import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from files_processor import process_files
from vector_store import VectorStore
from rag import ask

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

store = VectorStore()
loaded_files = []
history = []


class QuestionRequest(BaseModel):
    question: str


@app.get("/status")
def status():
    return {
        "files_loaded": len(loaded_files),
        "filenames": [os.path.basename(f) for f in loaded_files]
    }


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    global loaded_files, history

    ALLOWED = {".pdf", ".docx", ".txt", ".pptx"}
    saved_paths = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(path)

    chunks = process_files(saved_paths)
    store.add(chunks)

    loaded_files.extend(saved_paths)
    history = []

    return {
        "message": f"{len(saved_paths)} file(s) uploaded and processed",
        "filenames": [os.path.basename(p) for p in saved_paths],
        "chunks": len(chunks)
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not loaded_files:
        raise HTTPException(status_code=400, detail="No files loaded. Upload files first.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer, sources = ask(request.question, store, history)
    history.append({"question": request.question, "answer": answer})

    return {
        "answer": answer,
        "sources": sources
    }


@app.delete("/reset")
def reset():
    global loaded_files, history
    store.chunks = []
    store.embeddings = None
    loaded_files = []
    history = []
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return {"message": "All documents cleared"}