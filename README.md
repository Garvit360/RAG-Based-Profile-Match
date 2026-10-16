# RAG-Based Profile Matcher

Match job descriptions against resume PDFs using **section-aware chunking**, **OpenAI embeddings**, **ChromaDB**, and a **hybrid ranker** with must-have filters. Implements assignment Parts A (`resume_rag.py`) and B (`job_matcher.py`).

## Dataset

Resume PDFs ship as **`Resume.zip`**. Unzip before indexing:

```bash
unzip -o Resume.zip
```

The `Resume/` folder is gitignored; the zip is the source of truth.

## Quick start

```bash
cd /path/to/Rag-Based-Profile-Matcher
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add OPENAI_API_KEY
```

### 1. Index resumes (Part A)

Uses **section-aware chunking** (`chunking.py`), metadata extraction, and Chroma collection **`resume_chunks`**.

```bash
python resume_rag.py
# or: python resume_rag.py /path/to/pdfs
```

**Re-indexing:** After you change resumes or chunking logic, wipe the store and index again:

```bash
rm -rf chroma_db
python resume_rag.py
```

Embedding model: **`text-embedding-3-small`**. Persist path: **`./chroma_db`**.

### 2. Match jobs (Part B)

```bash
python job_matcher.py "Senior Python developer. 5+ years experience. Required: Python, Django."
```

Output is JSON on stdout (`job_description`, `top_matches[]` with `resume_path` relative to project root, e.g. `Resume/10089434.pdf`).

### 3. Tests

```bash
pytest
```

## Commands

| Command | Description |
|---------|-------------|
| `python resume_rag.py` | Index PDFs from `Resume/` |
| `python job_matcher.py "<JD>"` | Top-10 matches as JSON |
| `pytest` | Unit tests (chunking + must-have rules) |

## Example run

Recorded setup for graders (reproduce locally with your API key):

| Field | Value |
|-------|--------|
| Date | 2026-03-14 |
| Chunking | Section headers when detected; else recursive 512/50 (`Other`) |
| Embeddings | `text-embedding-3-small` |
| Vector store | Chroma `resume_chunks` in `./chroma_db` |
| Index command | `python resume_rag.py` |
| Match command | See below |

**Job description used:**

```text
Information Technology Specialist. 4+ years experience. Required: Python, technical support.
```

**Match command:**

```bash
python job_matcher.py "Information Technology Specialist. 4+ years experience. Required: Python, technical support."
```

**Sample output (truncated; scores vary with index):**

```json
{
  "job_description": "Information Technology Specialist. 4+ years experience. Required: Python, technical support.",
  "top_matches": [
    {
      "candidate_name": "…",
      "resume_path": "Resume/10089434.pdf",
      "match_score": 78,
      "matched_skills": ["Python", "…"],
      "relevant_excerpts": [
        "… experience with Python and IT support …",
        "…"
      ],
      "reasoning": "Strong match in Experience, Skills section(s). Matched skills: Python. Experience: 5 years."
    }
  ]
}
```

Run the index and matcher locally to replace placeholders with live results. Must-have rules:

- **Years:** `N+ years` / `minimum N years` → metadata `experience_years >= N` (unknown years fail).
- **Skills:** `Required:` / `Must have:` / `Skills:` lists → **every** listed skill must appear in resume metadata skills.

## Architecture (brief)

```text
Resume/*.pdf → resume_rag.py → Chroma (chunks + metadata)
Job description → job_matcher.py → semantic search → hybrid re-rank → must-have filter → JSON
```
