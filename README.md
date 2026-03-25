# Smart AI Assistant

An AI-powered assistant that answers questions from your own documents. Upload your files, ask questions in plain English, and get accurate answers with exact source references — no guessing, no hallucination.

---

## What It Does

- Upload any combination of PDF, Word, TXT, or PowerPoint files
- Ask questions about the content in natural language
- Get answers based strictly on your documents — not the internet
- See exactly which file and page number the answer came from
- Remembers previous questions in the same session for follow-up conversations

---

## How It Works

```
You upload documents
        ↓
Text is extracted from each file page by page
        ↓
Text is split into small overlapping chunks
        ↓
Each chunk is converted into embeddings (numerical vectors) locally
        ↓
You ask a question
        ↓
The question is also converted into an embedding
        ↓
Cosine similarity finds the most relevant chunks
        ↓
Top chunks are sent to LLaMA 3 (via Groq) as context
        ↓
LLaMA 3 generates an answer using only that context
        ↓
Answer is returned with file name and page number sources
```

---

## Project Architecture

```
rag_cli/
├── main.py              # FastAPI server — all API routes
├── files_processor.py   # Extracts and chunks text from all file types
├── vector_store.py      # Embeds chunks and searches by similarity
├── rag.py               # Sends context + question to LLaMA 3, returns answer
├── .env                 # API key (never shared or committed)
└── requirements.txt     # All dependencies
```

### API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/status` | Check which files are currently loaded |
| POST | `/upload` | Upload one or more documents |
| POST | `/ask` | Ask a question, get answer + sources |
| DELETE | `/reset` | Clear all loaded documents and memory |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| PDF Extraction | PyMuPDF |
| Word Extraction | python-docx |
| PowerPoint Extraction | python-pptx |
| Embeddings | sentence-transformers (runs locally) |
| Vector Search | NumPy cosine similarity |
| LLM | LLaMA 3.3 70B via Groq API (free) |

---

## Supported File Types

- `.pdf` — research papers, books, reports
- `.docx` — Word documents, notes
- `.txt` — plain text files
- `.pptx` — PowerPoint presentations

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/diya-garg18/Smart-AI-Assistant.git
cd Smart-AI-Assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key

- Go to [console.groq.com](https://console.groq.com)
- Sign up for free — no credit card required
- Go to API Keys and create a new key

### 4. Add your key

Create a `.env` file in the project folder:

```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the server

```bash
python -m uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

Interactive API docs available at `http://localhost:8000/docs`

---

## Using the API

### Upload files

```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf" \
  -F "files=@notes.docx"
```

### Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of this document?"}'
```

### Response

```json
{
  "answer": "The main topic is machine learning, specifically supervised learning methods (Page 3).",
  "sources": ["ml_book.pdf (Page 3)", "ml_book.pdf (Page 5)"]
}
```

### Check status

```bash
curl http://localhost:8000/status
```

### Reset

```bash
curl -X DELETE http://localhost:8000/reset
```