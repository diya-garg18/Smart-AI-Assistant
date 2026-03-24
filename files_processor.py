import os
import fitz
import docx

def process_files(paths):
    all_chunks = []
    for path in paths:
        print(f"  Processing: {os.path.basename(path)}")
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            chunks = _process_pdf(path)
        elif ext == ".docx":
            chunks = _process_docx(path)
        elif ext == ".txt":
            chunks = _process_txt(path)
        else:
            print(f"    -> Unsupported file type, skipping")
            continue
        all_chunks.extend(chunks)
        print(f"    -> {len(chunks)} chunks")
    return all_chunks

def _process_pdf(path):
    doc = fitz.open(path)
    chunks = []
    filename = os.path.basename(path)
    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text").strip()
        if not text:
            continue
        chunks.extend(_chunk_text(text, page_num + 1, filename))
    doc.close()
    return chunks

def _process_docx(path):
    doc = docx.Document(path)
    filename = os.path.basename(path)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return _chunk_text(full_text, 1, filename)

def _process_txt(path):
    filename = os.path.basename(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()
    return _chunk_text(text, 1, filename)

def _chunk_text(text, page, source):
    chunks = []
    size, overlap = 500, 100
    step = size - overlap
    for i in range(0, len(text), step):
        chunk = text[i:i+size].strip()
        if len(chunk) > 50:
            chunks.append({
                "text": chunk,
                "page": page,
                "source": source
            })
    return chunks