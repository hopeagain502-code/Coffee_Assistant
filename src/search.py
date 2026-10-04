import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Project folder = the folder above src/
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(os.path.join(BASE, "index", "coffee.faiss"))
chunks = json.load(open(os.path.join(BASE, "index", "chunks.json")))


def search(query, k=5, theme=None, per_file=2):
    q = model.encode([query], normalize_embeddings=True)
    q = np.array(q, dtype="float32")

    scores, ids = index.search(q, len(chunks))

    results = []
    count = {}
    for score, i in zip(scores[0], ids[0]):
        c = chunks[i]
        if theme and c["theme"] != theme:
            continue
        if count.get(c["source"], 0) >= per_file:
            continue
        count[c["source"]] = count.get(c["source"], 0) + 1
        results.append({**c, "score": float(score)})
        if len(results) == k:
            break
    return results


if __name__ == "__main__":
    print("Coffee search. Type a question (or 'quit' to stop).")
    print("To filter by topic: disease: how to control rust?\n")

    while True:
        text = input("Question: ").strip()
        if text.lower() in ("quit", "exit", ""):
            break

        theme = None
        if ":" in text:
            theme, text = text.split(":", 1)
            theme, text = theme.strip().lower(), text.strip()

        results = search(text, theme=theme)
        if not results:
            print("  No results. Check the topic word.\n")
            continue

        for r in results:
            print(f"\n  [{r['score']:.2f}] {r['source']}  (page {r['page']}, topic: {r['theme']})")
            print("   ", r["text"][:300], "...")
        print()