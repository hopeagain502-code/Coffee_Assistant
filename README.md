# Buna Assistant: Ethiopian Coffee Q&A with RAG

An AI assistant that answers questions about Ethiopian coffee **using only a set of documents**, and shows the sources behind every answer.

*Buna* is the word for coffee in Amharic and Afaan Oromo.

> **Screenshot:** add an image of the app here, for example `docs/screenshot.png`
>
> `![Buna Assistant](docs/screenshot.png)`

---

## 1. What is this project?

Normal chatbots can make up wrong answers (this is called *hallucination*) and they do not know your own documents.

This project uses **RAG (Retrieval-Augmented Generation)** to fix that:

1. **Retrieval:** the system finds the most relevant parts of the documents for a question.
2. **Generation:** a language model writes the answer using **only** those parts.
3. **Citations:** the app shows which file each answer came from.
4. **Refusal:** if the answer is not in the documents, the assistant says *"I don't know based on the documents."*

**Example**

> **Question:** What are the three rounds of the Ethiopian coffee ceremony?
> **Answer:** Abol, tona, and bereka, with frankincense burned during the ceremony [3].
> **Sources:** `brewing_ethiopian_cuisine.txt`

---

## 2. Why coffee?

Ethiopia is the birthplace of Arabica coffee, and coffee is an important crop and part of daily culture. A coffee assistant shows a real use case: helping farmers, students, and coffee lovers find information from trusted documents.

---

## 3. How it works

```
 Documents (PDF / TXT)
        |
        v
  ingest.py        read text, clean it, cut into 150-word chunks
        |           (each chunk keeps: file name, page, topic)
        v
  build_index.py   turn every chunk into 384 numbers (embedding)
        |           and store them in a FAISS index
        v
  index/coffee.faiss + index/chunks.json     (saved on disk)

 User question
        |
        v
  search.py        embed the question, find the closest chunks
        |           (optional topic filter, max 2 chunks per file)
        v
  chat.py          send the question + top 5 chunks to the LLM
        |           "answer ONLY from this context, cite sources"
        v
  Answer + sources  (shown in the Streamlit app)
```

### The steps in simple words

| Step | What happens |
|---|---|
| **Chunking** | Long documents are cut into small pieces of about 150 words, with 30 words of overlap so ideas are not cut in half. |
| **Embedding** | Each chunk is turned into a list of numbers that captures its meaning. Similar meaning gives similar numbers. |
| **Vector search** | FAISS compares the question with all chunks and returns the closest ones. |
| **Topic filter** | The first word of each file name is its topic (`disease_...`, `growing_...`), so users can search one topic only. |
| **Answer** | The LLM reads the best chunks and writes a short answer in simple English with citation numbers. |

---

## 4. Tech stack

| Purpose | Tool |
|---|---|
| Language | Python 3.12 / 3.13 |
| Read PDFs | `pypdf` |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector search | `faiss-cpu` |
| LLM | Groq API (`openai/gpt-oss-20b` by default, set in `.env`) |
| Web app | Streamlit |
| Data download | `wikipedia-api` |

No GPU is needed. Everything runs on a normal laptop CPU.

---

## 5. Project structure

```
buna-assistant/
├── app.py                  Streamlit web app
├── requirements.txt        Python packages
├── .env                    API key (NOT uploaded to GitHub)
├── .gitignore
├── data/                   PDFs and text files (one topic word first in each name)
├── index/                  Saved FAISS index and chunks (created by build_index.py)
├── tests/
│   ├── questions.csv       42 test questions
│   └── results.csv         Results of the last evaluation
└── src/
    ├── download_wiki.py    Download Wikipedia articles as text files
    ├── ingest.py           Read files, clean text, make chunks
    ├── build_index.py      Create embeddings and the FAISS index
    ├── search.py           Search the index
    ├── chat.py             Ask the LLM and return answer + sources
    ├── check_questions.py  Check test keywords exist in the data
    ├── evaluate.py         Score the chatbot on the test questions
    └── list_models.py      List the LLM models available for the API key
```

---

## 6. Data

### Sources

| Source | Content | License |
|---|---|---|
| **Wikipedia** | Coffee-related articles (coffee production in Ethiopia, Coffea arabica, coffee leaf rust, Colletotrichum kahawae, coffee berry borer, coffee processing, roasting, cupping, preparation, Yirgacheffe, Harar, Ethiopian cuisine, coffee cherry) | CC BY-SA 4.0 |
| **Starter notes (optional)** | Short summaries written for testing the pipeline. They are not official publications. | Own work |

Wikipedia text is licensed CC BY-SA 4.0. If you reuse the text, credit Wikipedia and share under the same license.

### File naming rule

The **first word** of each file name is the topic label used by the filter:

```
disease_coffee_leaf_rust.txt      ->  topic: disease
growing_coffee_production.txt     ->  topic: growing
brewing_ethiopian_cuisine.txt     ->  topic: brewing
```

Topics: `varieties`, `growing`, `disease`, `harvest`, `processing`, `storage`, `quality`, `brewing`.

### Adding real documents

Open-access research papers and reports (for example from journals such as MDPI and Frontiers, or from FAO and CGIAR) can be added the same way. Check the license first, rename the file with the topic first, put it in `data/`, and rebuild the index.

---

## 7. Setup

### 1. Get the code

```bash
git clone https://github.com/<your-username>/buna-assistant.git
cd buna-assistant
```

### 2. Install the packages

```bash
python -m pip install -r requirements.txt
```

Example `requirements.txt`:

```
pypdf
numpy
sentence-transformers
faiss-cpu
streamlit
groq
wikipedia-api
```

The first time you build the index, the embedding model (about 90 MB) is downloaded once.

### 3. Add your API key

Create a free key at [console.groq.com](https://console.groq.com), then create a file named `.env` in the project folder:

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Run `python src/list_models.py` to see which models your key can use. Never upload `.env` to GitHub.

### 4. Get the data

```bash
python src/download_wiki.py
```

This saves Wikipedia articles into `data/`. You can also add your own PDFs or text files.

### 5. Build the index

```bash
python src/ingest.py        # check: shows pages read and chunks created
python src/build_index.py   # creates index/coffee.faiss and index/chunks.json
```

Run `build_index.py` again every time you change the files in `data/` or the chunk size.

### 6. Run it

Command line chat:

```bash
python src/chat.py
```

Web app:

```bash
python -m streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

To filter by topic in the command line, type the topic before a colon: `disease: how do I prevent leaf rust?`

---

## 8. Design decisions

| Decision | Reason |
|---|---|
| **Chunk size 150 words** | The embedding model reads only about 256 tokens. Longer chunks would have their ends ignored. |
| **Overlap of 30 words** | Keeps sentences and ideas from being cut at chunk borders. |
| **Normalized embeddings + inner product** | Makes the search score work like cosine similarity (closer to 1 is a better match). |
| **Maximum 2 chunks per file** | Stops one long file from filling all result slots, so answers use several sources. |
| **Return 5 chunks** | Gives the LLM enough context without too much noise. |
| **Temperature 0** | Makes answers consistent and reduces creative guessing. |
| **Strict system prompt** | Forces the model to use only the context, cite sources, and refuse when the answer is missing. |
| **Metadata saved separately** | FAISS stores only numbers, so text, source, page, and topic are kept in `chunks.json`. |

---

## 9. Evaluation

I wrote **42 test questions** in `tests/questions.csv`:

- **36 answerable questions** about diseases, pests, species, caffeine, processing, roasting, cupping, brewing, Ethiopian regions, and the coffee ceremony.
- **6 out-of-scope questions** (for example "What is the capital of France?") that the assistant must refuse.

Each answerable question has an expected source file and a list of keywords that a correct answer should contain. `src/check_questions.py` first checks that those keywords really exist in the data, and `src/evaluate.py` runs the chatbot and scores it.

### Results

| Group | Questions | Retrieval (right file found) | Correct answer |
|---|---|---|---|
| Answerable | 36 | 32 / 36 (89%) | 30 / 36 (83%) |
| Out of scope (must refuse) | 6 | 6 / 6 (100%) | 6 / 6 (100%) |

- **Retrieval** means the expected source file was among the top 5 results.
- **Correct** means the answer contained at least one expected keyword.
- **Refusal** means the answer contained "I don't know".

### Experiments (fill in your own results)

| Setting | Retrieval | Correct |
|---|---|---|
| Chunk size 150, k = 5 (current) | 89% | 83% |
| Chunk size 100 | ? | ? |
| Chunk size 250 | ? | ? |
| k = 7 | ? | ? |

---

## 10. Limitations (please read)

- **Own test set.** The questions were written by me, not by an independent group, and the keyword scoring is simple. A correct answer in different words can be marked wrong, and a wrong answer with a lucky keyword can be marked right. Treat the scores as a development check, not a benchmark.
- **Small data.** The knowledge base is a small set of Wikipedia articles, so many coffee topics (for example detailed farming practices) are not covered well.
- **Wikipedia is not a farming manual.** The answers are general information. They are not professional agricultural advice.
- **Mixing of general facts.** The language model sometimes adds general coffee facts that are not about Ethiopia. The system prompt tries to prevent this, but answers should still be checked against the cited sources.
- **No page numbers for text files.** Text files are treated as one page, so the citation shows file name only.
- **English only.** Amharic and Afaan Oromo questions are not supported yet.
- **Internet needed.** The LLM call needs an internet connection and a Groq API key. Free tiers have rate limits.

**Safety note:** for pesticide or fungicide questions, always follow the product label and ask a local agricultural extension officer.

---

## 11. Possible improvements

- Add real research papers and manuals (open-access, with clear licenses) as sources.
- Remove reference lists from papers during ingestion.
- Try hybrid search (keyword + embeddings) and a re-ranking step.
- Add Amharic and Afaan Oromo support with a multilingual embedding model.
- Add a better evaluation: more questions, answers checked by a person, and a second model as a judge.
- Add image-based disease recognition for coffee leaves (needs a suitable, licensed image dataset).
- Show citation numbers next to each source in the app.

---

## 12. Deployment (Hugging Face Spaces)

1. Create a new Space and choose Streamlit.
2. Upload the project files (without `.env` and without the API key).
3. Add `GROQ_API_KEY` and `GROQ_MODEL` as **Secrets** in the Space settings.
4. Include `data/` or run `download_wiki.py` and `build_index.py` at start-up so the index exists.

---

## 13. What I learned

- How text is split, embedded, and searched with FAISS.
- Why chunk size and overlap matter for retrieval.
- How to write a prompt that forces grounded answers and refusals.
- How to build and score a test set, and why honest evaluation matters.
- How to keep secrets (API keys) out of code and GitHub.
- How to debug environment problems (Python interpreters, offline model loading, API model access).

---

## 14. Credits and license

- Wikipedia contributors, text under CC BY-SA 4.0.
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
- Vector search: FAISS by Meta AI Research.
- LLM access: Groq.

Code license: choose one (for example MIT) and add a `LICENSE` file.

**Author:** your name here
**Contact:** your email or LinkedIn here
