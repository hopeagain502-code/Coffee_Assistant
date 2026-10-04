import os
from groq import Groq

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for line in open(os.path.join(BASE, ".env")):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v.strip('"'))

client = Groq(api_key=os.environ["GROQ_API_KEY"])
for m in client.models.list().data:
    print(m.id)


def pick_model():
    """Use GROQ_MODEL if set, otherwise the first usable chat model."""
    if os.environ.get("GROQ_MODEL"):
        return os.environ["GROQ_MODEL"]
    skip = ("whisper", "guard", "tts", "playai", "compound")
    for m in client.models.list().data:
        if not any(s in m.id.lower() for s in skip):
            return m.id
    raise SystemExit("No chat models available for this API key. Check the Groq console.")


MODEL = pick_model()