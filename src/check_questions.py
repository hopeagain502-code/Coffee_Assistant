
import os
import csv
from ingest import load_pdfs, DATA_DIR

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(BASE, "tests", "questions.csv"), encoding="utf-8")))


def norm(t):
    return t.lower().replace("\u2019", "'")


text_by_file = {}
for p in load_pdfs(DATA_DIR):
    f = p["source"].lower()
    text_by_file[f] = text_by_file.get(f, "") + " " + norm(p["text"])

problems = 0
for row in rows:
    if row["should_refuse"].strip().lower() == "yes":
        continue
    exp = row["expected_source"].strip().lower()
    files = [f for f in text_by_file if exp in f] if exp else list(text_by_file)
    if not files:
        print(f"NO FILE    | '{exp}' matches no file | {row['question']}")
        problems += 1
        continue
    text = " ".join(text_by_file[f] for f in files)
    keys = [k.strip().lower() for k in row["keywords"].split("|") if k.strip()]
    if not any(k in text for k in keys):
        print(f"NO KEYWORD | none of {keys} found in {files} | {row['question']}")
        problems += 1

print(f"\nChecked {len(rows)} questions. Problems: {problems}")
print("Files in data/:", ", ".join(sorted(text_by_file)))
