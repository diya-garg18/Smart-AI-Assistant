# Smart AI Assistant — RAG CLI (Version 1: Single PDF)

An AI assistant that answers questions from a PDF document using Retrieval-Augmented Generation (RAG). Runs entirely in the terminal — no frontend, no server.

## How It Works
```
You upload a PDF
      ↓
Text is extracted page by page
      ↓
Split into overlapping chunks
      ↓
Each chunk is converted into embeddings (numbers) locally
      ↓
You ask a question
      ↓
Most relevant chunks are retrieved using cosine similarity
      ↓
Sent to LLaMA 3 (via Groq) to generate an answer
      ↓
Answer + page sources printed in terminal
```

## Project Structure
```
rag_cli/
├── main.py            # Run this
├── pdf_processor.py   # Extracts and chunks text from PDF
├── vector_store.py    # Embeds chunks, searches by similarity
├── rag.py             # Retrieves context, calls Groq API
├── .env               # Your API key (never commit this)
└── requirements.txt
```

## Setup

1. Install dependencies
```
pip install -r requirements.txt
```

2. Get a free Groq API key at [console.groq.com](https://console.groq.com)

3. Add your key to `.env`
```
GROQ_API_KEY=gsk_your_key_here
```

4. Run
```
python main.py
```

## Tech Stack

| Component | Tool |
|-----------|------|
| PDF Extraction | PyMuPDF |
| Embeddings | sentence-transformers (runs locally) |
| Vector Search | NumPy cosine similarity |
| LLM | LLaMA 3.3 70B via Groq (free) |

## Versions Planned

| Version | Description |
|---------|-------------|
| v1 (current) | Single PDF |
| v2 | Multiple PDFs |
| v3 | PDF + Word docs |
| v4 | PDF + Word + TXT |
| v5 | All file types including PPT |
```

---
