# Smart AI Assistant (CLI + Web UI)

An AI-powered assistant that answers questions from your own documents.
Load your files, ask questions in plain English, and get accurate answers with sources.

---

## 🚀 Features

* Works in **terminal (CLI)** or **browser (Web UI)**
* Supports multiple file types:

  * PDF
  * DOCX
  * TXT
  * PPTX
* Answers strictly based on your documents (no hallucination)
* Shows sources for every answer
* Keeps conversation history in session

---

## 🧠 How It Works

```
You load documents
        ↓
Text is extracted and split into chunks
        ↓
Each chunk → embedding (vector)
        ↓
Stored locally in vector store
        ↓
You ask a question
        ↓
Relevant chunks are retrieved
        ↓
Sent to LLM (LLaMA via Groq)
        ↓
Answer generated with sources
```

---

## 📁 Project Structure

```
rag_cli/
├── main.py              # CLI version (run in terminal)
├── backend.py          # Flask server for web UI
├── files_processor.py  # Extracts + chunks text
├── vector_store.py     # Embeddings + similarity search
├── rag.py              # LLM interaction
├── static/             # Frontend (HTML, JS, CSS)
├── uploads/            # Uploaded files
├── .env                # API key (not committed)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/diya-garg18/Smart-AI-Assistant.git
cd Smart-AI-Assistant
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Add API key

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ How to Run

You can run the project in **two ways**:

---

# 🟢 Option 1 — CLI (Recommended)

Run:

```bash
python main.py
```

Then enter file paths:

```
Enter file paths (comma separated):
C:\Users\YourName\Desktop\file.pdf
```

Ask questions:

```
You: summarize this document
```

---

# 🌐 Option 2 — Web UI

### Step 1: Start backend

```bash
python backend.py
```

---

### Step 2: Open in browser

```
http://127.0.0.1:5000
```

---

## 💬 Commands (CLI)

* `exit` → quit program
* `sources` → list loaded files

---

## 📄 Supported File Types

* `.pdf`
* `.docx`
* `.txt`
* `.pptx`

---

## 🧰 Tech Stack

| Layer         | Technology            |
| ------------- | --------------------- |
| Backend       | Flask                 |
| CLI           | Python                |
| Embeddings    | sentence-transformers |
| Vector Search | NumPy                 |
| LLM           | LLaMA (via Groq API)  |

---

## ⚠️ Notes

* First run downloads embedding model (~90MB)
* Do NOT commit `.env` file
* `.history/` and `uploads/` should be ignored in Git

---

## 🚀 Example

```
python main.py

Enter file paths:
notes.pdf

You: what is this about?
Answer: ...
Sources: ...
```

---

## 🔒 Security

* API keys are stored in `.env`
* Never commit `.env` or `.history/`
* If a key is exposed, regenerate it immediately

---
