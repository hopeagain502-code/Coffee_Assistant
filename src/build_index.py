import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from ingest import load_pdfs, split_into_chunks

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pages = load_pdfs(os.path.join(BASE, "data"))
chunks = split_into_chunks(pages)
print(f"Pages: {len(pages)}  Chunks: {len(chunks)}")

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
embeddings = np.array(embeddings, dtype="float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

out = os.path.join(BASE, "index")
os.makedirs(out, exist_ok=True)
faiss.write_index(index, os.path.join(out, "coffee.faiss"))
with open(os.path.join(out, "chunks.json"), "w") as f:
    json.dump(chunks, f)

print("Index saved in", out)