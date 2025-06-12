import os
from PyPDF2 import PdfReader

CHUNK_FOLDER = "data/pdf_chunks"
CHUNK_SIZE = 4500  # characters
CHUNK_OVERLAP = 300  # characters

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text.strip() + "\n\n"
    return text

def split_into_chunks(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def save_chunks(chunks, output_dir=CHUNK_FOLDER):
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        with open(os.path.join(output_dir, f"chunk_{i+1:02d}.txt"), "w", encoding="utf-8", errors="ignore") as f:
            f.write(chunk)


def chunk_pdf(pdf_path="data/chatbot_brokins2.pdf"):
    print("📄 Extracting and chunking PDF...")
    raw_text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(raw_text)
    save_chunks(chunks)
    print(f"✅ {len(chunks)} chunks saved in '{CHUNK_FOLDER}'")
    for i, chunk in enumerate(chunks):
        if "Generali" in chunk:
            print(f"✅ GENERALI found in chunk {i}")

if __name__ == "__main__":
    chunk_pdf()


