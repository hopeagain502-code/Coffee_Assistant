import os
import re
import wikipediaapi

wiki = wikipediaapi.Wikipedia(user_agent="buna-assistant (student project)", language="en")

# Wikipedia page title -> topic label (becomes the first word of the file name)
PAGES = {
    "Coffea arabica": "varieties",
    "Coffee production in Ethiopia": "growing",
    "Coffee": "growing",
    "Coffee cherry": "harvest",
    "Coffee leaf rust": "disease",
    "Hemileia vastatrix": "disease",
    "Colletotrichum kahawae": "disease",
    "Coffee berry borer": "disease",
    "Coffee processing": "processing",
    "Coffee roasting": "brewing",
    "Coffee cupping": "quality",
    "Coffee preparation": "brewing",
    "Ethiopian cuisine": "brewing",
    "Yirgacheffe": "growing",
    "Harar": "growing",
}

os.makedirs("data", exist_ok=True)

for title, theme in PAGES.items():
    page = wiki.page(title)
    if not page.exists():
        print("NOT FOUND:", title)
        continue
    name = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    path = f"data/{theme}_{name}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(page.text)
    print(f"saved {path}  ({len(page.text.split())} words)")