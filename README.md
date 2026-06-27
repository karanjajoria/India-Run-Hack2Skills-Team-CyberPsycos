<div align="center">

<img src="HireLens-Logo.png" alt="HireLens Logo" />

# HireLens
### Stop Guessing. Start Matching.

**AI-powered candidate ranking that thinks like a recruiter — not a search engine.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-HireLens-5B6EF5?style=for-the-badge)](https://hirelens-front-end.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3-F55036?style=for-the-badge)](https://groq.com)

</div>

---

## 🎯 The Problem

Recruiters spend **23% of their time** manually screening resumes. Keyword-based ATS systems miss great candidates who use different words for the same skills. The result? Good talent gets filtered out, and bad fits get through.

**HireLens fixes this.**

---

## ✨ What It Does

HireLens reads a job description the way a senior recruiter would — understanding *intent*, not just keywords — and ranks candidates using a hybrid AI engine that combines:

- 🧠 **Semantic understanding** — "built distributed APIs in Go" matches "backend scalability engineer"
- ✅ **Skill alignment** — must-haves vs nice-to-haves, weighted separately
- 📈 **Experience quality** — years, domain relevance, career progression
- 💡 **Explainability** — every ranking decision comes with a human-readable reason

**Upload a JD. Upload resumes (PDF/DOCX) or paste text. Get a ranked shortlist with explanations in under 60 seconds.**

---

## 🚀 Live Demo

**[👉 Try HireLens now](https://hirelens-front-end.onrender.com/)**

> ⚠️ The backend runs on Render's free tier and may take **30–50 seconds to wake up** on the first request. Subsequent requests are fast. In addition to this, it will be active for the next 60 days **Only**

---

## 🖥️ Screenshots

### Step 1 — Paste or Upload Your JD & Multiple Candidates

<img src="img\image.png" alt="HireLens Upload Page — ranking in progress" width="100%" />

**What you're seeing:**
- **Job Description (left)** — The full JD for an **ML Intern — Computer Vision** role is pasted directly as text. You can also upload a PDF or DOCX file using the toggle.
- **Candidates (right)** — Two resumes uploaded simultaneously as PDF files: `ML_resume.pdf` (147KB) and `resume_1_aryan_sharma.pdf` (5KB). HireLens supports **Files**, **Text paste**, or **Both** modes — so recruiters can mix uploaded PDFs with pasted profiles in the same session.
- **Ranking in progress** — The "Ranking candidates..." button shows the live pipeline running: parsing documents → generating embeddings → scoring candidates. Takes 20–60 seconds depending on candidate count.

> 💡 **For recruiters:** No formatting required. Paste raw text, upload any PDF/DOCX, or mix both. HireLens handles messy, unstructured resumes.

---

### Step 2 — Side-by-Side Candidate Comparison

<img src="img\image1.png" alt="HireLens Results Page — 2 candidates ranked" width="100%" />

**What you're seeing:**

**Top bar** — Processed 2 candidates in 52.54s · 2 Shortlisted · 0 Strong Fit · 1 Good Fit · Top Score 77 · One-click **Export CSV**

**Job Summary Card** — HireLens auto-extracted from the JD:
- Role: ML Intern — Computer Vision · Domain: Computer Science (AI/ML) · Seniority: Junior
- 16 must-have skills identified: Python, SQL, Pandas, NumPy, Matplotlib, Seaborn, Git, PyTorch, TensorFlow, Keras, Scikit-Learn, LSTM, CNN, RNN, Clustering, Anomaly Detection, FastAPI, Flask, Docker, REST APIs, ETL Pipelines

**Candidate #1 — Karan Jajoria** `Good · 77/100`
- Semantic: 100 · Skills: 91 · Experience: 87 · Recency: 18
- ✅ Matched 13 must-have skills · ❌ Missing: Git
- AI highlights: YOLOv8/OpenCV for computer vision · FastAPI + Docker deployment · LLaMA 3 RAG integration

**Candidate #2 — Aryan Sharma** `Moderate · 49/100`
- Strong in LLM fine-tuning and NLP but weak on computer vision concepts (CNN, Anomaly Detection)
- AI highlights: 2 years full-time industry experience · RAG architecture · Healthcare and fintech AI delivery
- Missing key CV skills — correctly ranked lower for this specific role

> 💡 **For recruiters:** The side-by-side view instantly shows *why* one candidate ranks higher — not just a number, but matched skills, missing must-haves, and an AI-written evaluation note.

---

### 📋 Output — CSV Export (Real Data)

Click **Export CSV** on any results page to download a recruiter-ready file. Here's the actual output from the session above:

| Rank | Name | Score | Fit Band | Semantic | Skill Match | Experience | Recency | Matched Skills | Missing Must-Haves | Explanation |
|------|------|-------|----------|----------|-------------|------------|---------|----------------|--------------------|-------------|
| 1 | Karan Jajoria | 77.1 | Good | 100 | 91.0 | 87.0 | 18 | Python; SQL; Pandas; NumPy; Matplotlib; Seaborn; PyTorch; TensorFlow; Keras; Scikit-Learn; LSTM; CNN; RNN; Clustering; Anomaly Detection | Git | Strong candidate with hands-on production experience in computer vision and LLM integration. Lack of Git experience and slightly lower overall score (77/100) prevent top-tier ranking. Proven track record of shipping real-world AI pipelines. |
| 2 | Aryan Sharma | 49.0 | Moderate | 68 | 42.0 | 57.0 | 12 | Python; PyTorch; TensorFlow; FastAPI; Docker | Git; CNN; RNN; LSTM; Anomaly Detection; Clustering; Scikit-Learn; Seaborn | Strong foundation in LLM fine-tuning and scalable inference pipelines. Lack of experience with key computer vision concepts (CNN, Anomaly Detection) limits fit for this specific role. |

> Every column is auto-populated — zero manual effort from the recruiter.

---

## 🏗️ Architecture

```
Job Description + Resumes
          │
          ▼
┌─────────────────────────┐
│   Document Parser       │  PDF · DOCX · TXT · paste text
└────────────┬────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌─────────┐    ┌─────────────┐
│ LLM     │    │  Structured │
│ (Groq   │───►│  Profiles   │
│ LLaMA3) │    └──────┬──────┘
└─────────┘           │
             ┌────────┴─────────┐
             ▼                  ▼
    ┌──────────────┐   ┌────────────────┐
    │  Embeddings  │   │ Feature Extract│
    │ MiniLM-L6-v2 │   │ Skills · Years │
    └──────┬───────┘   │ Domain · Recy. │
           │           └───────┬────────┘
           ▼                   │
    ┌──────────────┐           │
    │   Qdrant     │◄──────────┘
    │ (on-disk)    │  Store + Search
    └──────┬───────┘
           │  Top-K retrieved
           ▼
    ┌──────────────────────────┐
    │   Hybrid Reranker        │
    │   35% Semantic fit       │
    │   25% Skill match        │
    │   20% Experience         │
    │   10% Recency            │
    │   10% Behavioral signals │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────┐
    │  Explanation │  Groq LLaMA 3 → recruiter note + highlights
    │  Generator   │
    └──────┬───────┘
           │
           ▼
    Ranked Shortlist  ·  Score Breakdown  ·  CSV Export
```

---

## 🧰 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | FastAPI (Python) | Fast, async, auto-docs |
| LLM | Groq — LLaMA 3 8B | Free tier, blazing fast inference |
| Embeddings | `all-MiniLM-L6-v2` | Lightweight, highly accurate semantic matching |
| Vector DB | Qdrant (on-disk) | No cloud needed, persistent, production-grade |
| Frontend | React + Vite + Tailwind | Polished, responsive UI |
| Deployment | Render | Free, zero-config |

---

## 📊 Scoring Model

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Semantic Fit | **35%** | Cosine similarity of JD ↔ candidate embeddings |
| Skill Match | **25%** | Must-have (70%) + preferred skills (30%) overlap |
| Experience Relevance | **20%** | Years ratio + domain keyword match in roles |
| Recency & Progression | **10%** | Recent role relevance + career depth |
| Behavioral Signals | **10%** | Trait keyword match from JD behavioral indicators |

Candidates are assigned a **fit band**: `Strong (80+)` · `Good (65+)` · `Moderate (45+)` · `Weak`

---

## ⚡ Run Locally

### Prerequisites
- Python 3.10+
- Node.js 20+
- Free [Groq API key](https://console.groq.com)

### Backend
```bash
cd backend
cp .env.example .env
# Add GROQ_API_KEY to .env

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

> Run both terminals **simultaneously** — backend on port 8000, frontend on port 3000.

---

## 🐳 Docker (One Command)

```bash
echo "GROQ_API_KEY=your_key_here" > .env
docker-compose up --build
# App → http://localhost
# API docs → http://localhost:8000/docs
```

---

## 📁 Project Structure

```
HireLens/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # FastAPI endpoints
│   │   ├── core/config.py         # Settings & env vars
│   │   ├── models/schemas.py      # Pydantic models
│   │   └── services/
│   │       ├── parser.py          # PDF/DOCX/TXT extraction
│   │       ├── llm.py             # Groq LLM calls
│   │       ├── embeddings.py      # SentenceTransformers
│   │       ├── vector_store.py    # Qdrant client
│   │       └── ranker.py          # Core hybrid ranking engine
│   ├── main.py
│   ├── requirements.txt
│   ├── runtime.txt                # Python 3.10.11
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   ├── HireLens-Logo-only.png
│   │   ├── screenshot-upload.png
│   │   └── screenshot-results.png
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx     # JD + candidate input UI
│   │   │   └── ResultsPage.jsx    # Ranked results + export
│   │   ├── lib/api.js             # Fetch-based API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .nvmrc                     # Node 20.11.0
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🌐 Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Render Static Site | [hirelens-front-end.onrender.com](https://hirelens-front-end.onrender.com/) |
| Backend | Render Web Service | [hirelens-wl1a.onrender.com](https://hirelens-wl1a.onrender.com/) |

---

## 🏆 Built For

This project was built for **India Run — Hack2Skill Hackathon** as a solution to the intelligent candidate screening problem statement.

**What makes it stand out:**
- Goes beyond keyword matching with true semantic understanding
- Hybrid scoring mirrors how experienced recruiters actually evaluate candidates
- Every decision is explainable — no black box
- Supports PDF, DOCX, TXT uploads and pasted text simultaneously
- Production-ready architecture with vector search, LLM parsing, and a polished UI

---

## 📬 Contact

Built with ❤️ by **Karan Jajoria**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Karan_Jajoria-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/karanjajoria/)
[![GitHub](https://img.shields.io/badge/GitHub-karanjajoria-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/karanjajoria)

---

<div align="center">
<sub>If HireLens helped you or impressed you, consider giving it a ⭐ on GitHub!</sub>
</div>