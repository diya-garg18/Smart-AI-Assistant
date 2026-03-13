import fitz

def process_pdf(path):
    doc = fitz.open(path)
    chunks = []
    filename = os.path.basename(path)

    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text").strip()
        if not text:
            continue

        # Split page into chunks of ~500 chars with 100 overlap
        size, overlap = 500, 100
        step = size - overlap
        for i in range(0, len(text), step):
            chunk = text[i:i+size].strip()
            if len(chunk) > 50:
                chunks.append({
                    "text": chunk,
                    "page": page_num + 1,
                    "source": path
                })

    doc.close()
    return chunks

import os
