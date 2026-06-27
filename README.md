# TalentIQ — Hybrid Candidate Ranking Engine

> AI-powered recruiter tool that ranks candidates using semantic similarity, skill alignment, and experience quality — with human-readable explanations for every decision.

---

## Architecture

```
JD + Resumes
     │
     ▼
┌─────────────────────────────────────────────┐
│  Document Parser (PDF / DOCX / TXT / text)  │
└────────────────────┬────────────────────────┘
                     │
     ┌───────────────┴────────────────┐
     ▼                                ▼
┌──────────┐                   ┌──────────────┐
│ LLM Parse│  Groq LLaMA 3     │  Structured  │
│  (Groq)  │ ─────────────►   │   Profiles   │
└──────────┘                   └──────┬───────┘
                                      │
                     ┌────────────────┴──────────────┐
                     ▼                               ▼
           ┌─────────────────┐           ┌──────────────────┐
           │  Embeddings     │           │  Feature Extract │
           │  (MiniLM-L6-v2) │           │  Skill overlap   │
           └────────┬────────┘           │  Exp. years      │
                    │                    │  Recency         │
                    ▼                    └────────┬─────────┘
           ┌─────────────────┐                   │
           │  Qdrant         │◄──────────────────┘
           │  (on-disk)      │  Store + search
           └────────┬────────┘
                    │  Top-K retrieved
                    ▼
           ┌─────────────────────────────┐
           │  Hybrid Reranker            │
           │  35% Semantic               │
           │  25% Skill match            │
           │  20% Experience relevance   │
           │  10% Recency/progression    │
           │  10% Behavioral signals     │
           └────────┬────────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  Explanation    │  Groq LLaMA 3
           │  Generator      │─────────────►  Recruiter note + highlights
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  Ranked Output  │  JSON + CSV export
           └─────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| LLM | Groq — LLaMA 3 8B (free tier) |
| Embeddings | `all-MiniLM-L6-v2` via SentenceTransformers |
| Vector DB | Qdrant (on-disk mode) |
| Frontend | React + Vite + Tailwind CSS |
| Deployment | Docker + Docker Compose |

---

## Quick Start (Local Dev)

### 1. Get a free Groq API key
Sign up at [console.groq.com](https://console.groq.com) — free tier includes LLaMA 3.

### 2. Backend
```bash
cd backend
cp .env.example .env
# Add your GROQ_API_KEY to .env

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## Docker Deployment (Production)

```bash
# 1. Set your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 2. Build and run
docker-compose up --build

# App is live at http://localhost
# API docs at http://localhost:8000/docs
```

---

## Usage

1. **Upload or paste a Job Description** — the system extracts title, must-have skills, preferred skills, seniority, domain, and behavioral traits.

2. **Upload resumes (PDF/DOCX) or paste candidate profiles** — supports both simultaneously.

3. **Click "Rank Candidates"** — the pipeline runs in ~20–60 seconds depending on number of candidates.

4. **View the ranked shortlist** — each candidate shows:
   - Overall score (0–100) with fit band (Strong / Good / Moderate / Weak)
   - Radar chart of score dimensions
   - Matched and missing skills
   - AI-generated recruiter explanation
   - Key highlights

5. **Export CSV** for recruiter handoff.

---

## Scoring Weights

| Dimension | Weight | Signal |
|-----------|--------|--------|
| Semantic Fit | 35% | Cosine similarity of JD ↔ candidate embeddings |
| Skill Match | 25% | Must-have (70%) + preferred (30%) skill overlap |
| Experience Relevance | 20% | Years ratio + domain keyword match in roles |
| Recency & Progression | 10% | Recent role relevance + career depth |
| Behavioral Signals | 10% | Keyword match on behavioral traits from JD |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq LLM API key (free at console.groq.com) | — |
| `QDRANT_PATH` | On-disk path for Qdrant storage | `./qdrant_storage` |
| `COLLECTION_NAME` | Qdrant collection name | `talentiq_candidates` |
| `EMBEDDING_MODEL` | SentenceTransformers model | `all-MiniLM-L6-v2` |
| `TOP_K_RETRIEVE` | Candidates to retrieve from vector search | `50` |
| `TOP_K_SHORTLIST` | Final shortlist size | `10` |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/rank` | Main ranking endpoint (multipart form) |
| `POST` | `/api/export/csv` | Export results as CSV |
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Swagger UI |

---

## Notes on Groq Free Tier
- Rate limit: ~30 req/min on free tier
- Model: `llama3-8b-8192` (fast, capable)
- If no API key is set, the system falls back to heuristic parsing and skips LLM explanations — ranking still works via embeddings.

---

## Project Structure

```
talentiq/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # FastAPI endpoints
│   │   ├── core/config.py         # Settings
│   │   ├── models/schemas.py      # Pydantic models
│   │   └── services/
│   │       ├── parser.py          # PDF/DOCX extraction
│   │       ├── llm.py             # Groq LLM calls
│   │       ├── embeddings.py      # SentenceTransformers
│   │       ├── vector_store.py    # Qdrant client
│   │       └── ranker.py          # Core ranking engine
│   ├── main.py                    # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx     # Upload + input UI
│   │   │   └── ResultsPage.jsx    # Ranked results UI
│   │   ├── lib/api.js             # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```
