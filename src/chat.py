import os
from groq import Groq
from search import search

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    """Read KEY=value lines from the .env file."""
    path = os.path.join(BASE, ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


load_env()

if "GROQ_API_KEY" not in os.environ:
    raise SystemExit("GROQ_API_KEY is missing. Put it in the .env file.")

# This model is available for your key. Change it in .env with GROQ_MODEL=...
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM = (
    "You are a coffee assistant for Ethiopian coffee. "
    "Answer ONLY using the numbered context below. "
    "Use only facts that are about Ethiopia or that the context clearly connects to Ethiopia. "
    "Do not add general facts about other countries. "
    "If the answer is not in the context, say: I don't know based on the documents. "
    "Use simple English. Cite sources like [1] or [2] after each fact. "
    "For pesticide or fungicide questions, add: follow the product label and ask a local extension officer."
)


def answer(question, theme=None, k=5):
    results = search(question, k=k, theme=theme)
    if not results:
        return "I don't know based on the documents.", []

    context = "\n\n".join(
        f"[{i}] ({r['source']}, page {r['page']})\n{r['text']}"
        for i, r in enumerate(results, start=1)
    )
    try:
        reply = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
        )
        return reply.choices[0].message.content, results
    except Exception as e:
        # If the LLM fails, still show the best passages instead of crashing
        passages = "\n\n".join(f"[{i}] {r['text'][:400]}" for i, r in enumerate(results, 1))
        return f"(LLM unavailable: {type(e).__name__}. Best passages:)\n\n{passages}", results


if __name__ == "__main__":
    print("Coffee assistant. Type a question (or 'quit').")
    print("Optional topic filter:  disease: how do I prevent rust?\n")
    while True:
        text = input("Question: ").strip()
        if text.lower() in ("quit", "exit", ""):
            break
        theme = None
        if ":" in text:
            theme, text = text.split(":", 1)
            theme, text = theme.strip().lower(), text.strip()

        text_answer, results = answer(text, theme=theme)
        print("\nANSWER:\n" + text_answer)

        print("\nSOURCES:")
        seen = set()
        for r in results:
            key = (r["source"], r["page"])
            if key not in seen:
                seen.add(key)
                print(f"  {r['source']} (page {r['page']})")
        print()