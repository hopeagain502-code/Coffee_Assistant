
import os
import csv
import time
from collections import defaultdict
from chat import answer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(BASE, "tests", "questions.csv"), encoding="utf-8")))

stats = defaultdict(lambda: {"n": 0, "retrieved": 0, "correct": 0})
report = []

for row in rows:
    q = row["question"]
    refuse = row["should_refuse"].strip().lower() == "yes"
    text, results = answer(q)
    text_l = text.lower().replace("\u2019", "'")
    sources = " ".join(r["source"].lower() for r in results)

    if refuse:
        group = "refusal"
        retrieved = True
        correct = "don't know" in text_l
    else:
        group = "answerable"
        exp = row["expected_source"].strip().lower()
        retrieved = (exp in sources) if exp else True
        keys = [k.strip().lower() for k in row["keywords"].split("|") if k.strip()]
        correct = any(k in text_l for k in keys) if keys else False

    stats[group]["n"] += 1
    stats[group]["retrieved"] += int(retrieved)
    stats[group]["correct"] += int(correct)
    report.append((q, group, retrieved, correct))
    print(f"{'OK  ' if correct else 'FAIL'} | retrieved={retrieved} | {q}")
    time.sleep(2)

print("\n=== RESULTS ===")
for group, s in stats.items():
    n = s["n"]
    print(f"{group}: {n} questions | retrieval {s['retrieved']}/{n} "
          f"({100 * s['retrieved'] / n:.0f}%) | correct {s['correct']}/{n} "
          f"({100 * s['correct'] / n:.0f}%)")

with open(os.path.join(BASE, "tests", "results.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["question", "group", "retrieved_right_file", "correct"])
    w.writerows(report)
print("\nSaved tests/results.csv")
