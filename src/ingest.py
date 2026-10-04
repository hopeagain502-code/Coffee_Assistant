import os
import re
from pypdf import PdfReader

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")


def get_theme(filename):
    """growing_coffee_guide.pdf -> growing"""
    return filename.split("_")[0].lower()


def clean_text(text):
    """Fix spaces and remove the starter-notes warning."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"STARTER NOTES.*?final\s*project\s*\.", "", text, flags=re.IGNORECASE)
    return text.strip()


def load_pdfs(folder):
    """Read PDFs and text files from the folder."""
    pages = []
    for filename in sorted(os.listdir(folder)):
        path = os.path.join(folder, filename)

        if filename.endswith(".pdf"):
            reader = PdfReader(path)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    text = clean_text(text)
                    if text:
                        pages.append({"text": text, "source": filename,
                                      "page": page_num, "theme": get_theme(filename)})

        elif filename.endswith((".txt", ".md")):
            with open(path, encoding="utf-8") as f:
                text = clean_text(f.read())
            if text:
                pages.append({"text": text, "source": filename,
                              "page": 1, "theme": get_theme(filename)})
    return pages


def split_into_chunks(pages, chunk_size=150, overlap=30):
    chunks = []
    for p in pages:
        words = p["text"].split()
        start = 0
        while start < len(words):
            piece = " ".join(words[start:start + chunk_size])
            chunks.append({
                "text": piece,
                "source": p["source"],
                "page": p["page"],
                "theme": p["theme"],
            })
            start += chunk_size - overlap
    return chunks


if __name__ == "__main__":
    pages = load_pdfs(DATA_DIR)
    chunks = split_into_chunks(pages)
    print(f"Pages read: {len(pages)}")
    print(f"Chunks created: {len(chunks)}")
    if chunks:
        print("\nSample chunk:\n", chunks[0]["text"][:300])
    else:
        print("\nNo text found. Check that data/ has PDFs or .txt files.")