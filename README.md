# 🎤 InterviewAI — AI Mock Interview Platform

A voice-based AI interview platform that conducts realistic mock interviews across 8 technical domains. Built for backend developers with 2–4 years of experience preparing for product company interviews.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

---

## ✨ Features

- 🎤 **Voice interviews** — speak your answers, AI listens and responds
- 🤖 **AI interviewer personas** — each domain has a named interviewer with realistic behavior
- 📊 **Feedback reports** — score, strengths, improvements, full transcript
- 🔄 **LLM fallback chain** — Groq → Ollama (never goes down)
- 🔐 **JWT authentication** — register, login, session history
- 📱 **PWA** — installable on mobile as a native app

---

## 🗂️ Interview Types

| Domain | Topics |
|---|---|
| DSA & Algorithms | Arrays, Trees, DP, Graphs |
| System Design | Scalability, Caching, Architecture |
| Python Backend | FastAPI, Django, Flask, pytest |
| Databases & Messaging | PostgreSQL, Redis, Kafka, Celery |
| DevOps & Infrastructure | Docker, Kubernetes, Terraform, AWS |
| AI & LLM Engineering | RAG, LangChain, Prompt Engineering |
| System Concepts | Microservices, OAuth2, WebSockets |
| Behavioral / HR | STAR method, leadership, teamwork |

---

## 🛠️ Tech Stack

**Backend**
- FastAPI + SQLAlchemy (async)
- PostgreSQL
- JWT authentication (python-jose + bcrypt)
- Groq API (llama-3.3-70b-versatile) with Ollama fallback

**Frontend**
- Vanilla HTML/CSS/JS
- Web Speech API (STT + TTS) — no paid voice API
- PWA ready (installable on mobile)

**Infrastructure**
- Docker + Docker Compose (local)
- Railway (backend + PostgreSQL)
- Vercel (frontend)

---

## 🚀 Local Setup

### Prerequisites
- Docker Desktop
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Ollama installed locally (optional fallback)

### Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-interviewer.git
cd ai-interviewer

# 2. Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and add your GROQ_API_KEY

# 3. Start with Docker
docker compose up --build

# 4. Open frontend
# Open frontend/index.html in Chrome
```

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://interviewer:interviewer123@db:5432/interviewerdb
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, get JWT |
| GET | `/auth/me` | Get current user |
| POST | `/interview/start` | Start interview session |
| POST | `/interview/respond` | Submit answer, get AI response |
| POST | `/interview/end/{id}` | End session, generate feedback |
| GET | `/interview/sessions` | List past sessions |

---

## 🌐 Deployment

- **Backend** → Railway
- **Frontend** → Vercel

---

## 📁 Project Structure
```
ai-interviewer/
├── backend/
│   ├── app/
│   │   ├── routes/        # auth.py, interview.py
│   │   ├── main.py        # FastAPI app
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── llm_client.py  # Groq + Ollama fallback
│   │   └── prompts.py     # Interview system prompts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html         # Login + interview type selection
│   ├── interview.html     # Live voice interview
│   ├── report.html        # Feedback report
│   ├── manifest.json      # PWA manifest
│   └── sw.js              # Service worker
└── docker-compose.yml
```

---

## 👤 Author

**Nihal**
Python Backend Developer | Bengaluru
[LinkedIn](#) · [GitHub](#)