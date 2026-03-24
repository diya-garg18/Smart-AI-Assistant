import os
import fitz

def process_pdfs(paths):
    all_chunks = []
    for path in paths:
        print(f"  Processing: {os.path.basename(path)}")
        chunks = _process_single(path)
        all_chunks.extend(chunks)
        print(f"    -> {len(chunks)} chunks")
    return all_chunks

def _process_single(path):
    doc = fitz.open(path)
    chunks = []
    filename = os.path.basename(path)

    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text").strip()
        if not text:
            continue

        size, overlap = 500, 100
        step = size - overlap
        for i in range(0, len(text), step):
            chunk = text[i:i+size].strip()
            if len(chunk) > 50:
                chunks.append({
                    "text": chunk,
                    "page": page_num + 1,
                    "source": filename
                })

    doc.close()
    return chunks