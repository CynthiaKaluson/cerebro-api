# Cerebro API

```

A production-ready real-time AI conversation API. Engage your ideas in a
persistent Socratic dialogue — where the AI challenges assumptions, asks
probing questions, and streams responses token-by-token — secured with
JWT authentication and deployed on Render.
```

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Deployment](https://img.shields.io/badge/deployment-render-purple)

**Live API:** https://cerebro-api-qe3q.onrender.com

**Interactive Docs:** https://cerebro-api-qe3q.onrender.com/docs

---

## What is Cerebro?

```

Most AI tools generate ideas for you. Cerebro does the opposite.

It acts as a Socratic creative partner — one that challenges your thinking,
exposes hidden assumptions, and forces you to defend and refine your ideas
through structured dialogue. Every response streams back token-by-token in
real time over Server-Sent Events.
```

---

## Key Features

```

**SSE Streaming Engine** — AI responses stream token-by-token in real time
over Server-Sent Events. No waiting for the full response.

**Socratic AI Partner** — The AI is prompted to challenge, question, and
push ideas further. It does not generate content — it sharpens thinking.

**Persistent Idea Threads** — Users create idea threads and maintain full
conversation history stored in PostgreSQL. Every message is retrievable.

**JWT Authentication** — Secure registration, login, and protected endpoints
with token-based auth. Passwords hashed with bcrypt.

**Async Architecture** — Fully async request handling with SQLAlchemy 2.0
async and asyncpg for high-performance non-blocking database operations.

**Modular Backend Design** — Clean separation of endpoints, services,
models, schemas, and core logic. Production-ready project structure.
```

---

## Technical Stack

| Layer            | Technology                    |
| ---------------- | ----------------------------- |
| Framework        | FastAPI 0.115                 |
| Language         | Python 3.11                   |
| Database         | PostgreSQL 16 (Neon)          |
| ORM              | SQLAlchemy 2.0 async          |
| DB Driver        | asyncpg                       |
| AI Provider      | OpenAI GPT-4o-mini            |
| Auth             | JWT via python-jose + passlib |
| Streaming        | Server-Sent Events (SSE)      |
| Containerisation | Docker                        |
| Deployment       | Render                        |

---

## Architecture

Client Request
↓
FastAPI Router
↓
JWT Authentication
↓
Ideas / Messages Endpoint
↓
AI Service (OpenAI GPT-4o-mini)
↓
SSE Streaming Response ←→ PostgreSQL (message history)
↓
JSON / SSE API Response

### Why async?

Every endpoint uses `async/await` with SQLAlchemy 2.0 async and asyncpg.
This means database queries and AI API calls are non-blocking — the server
handles concurrent requests without waiting.

### Why SSE over WebSockets?

Server-Sent Events are simpler, work over standard HTTP, support automatic
reconnection, and are the correct tool for one-way server push — which is
exactly what streaming AI responses require.

### Why GPT-4o-mini?

Same reasoning capability as GPT-4o for conversational tasks at a fraction
of the cost. A deliberate architectural decision to keep the API sustainable
at scale.

---

## Project Structure

```

cerebro-api/
├── app/
│   ├── main.py                          # FastAPI app, lifespan, middleware
│   ├── config.py                        # Settings via pydantic-settings
│   ├── database.py                      # Async engine, session, Base
│   ├── models.py                        # SQLAlchemy models
│   ├── schemas.py                       # Pydantic request/response schemas
│   ├── core/
│   │   ├── security.py                  # Password hashing, JWT creation
│   │   └── dependencies.py             # get_current_user dependency
│   ├── api/v1/
│   │   ├── router.py                    # API router registration
│   │   └── endpoints/
│   │       ├── auth.py                  # Register, login, me
│   │       ├── ideas.py                 # Ideas CRUD
│   │       └── messages.py             # SSE streaming messages
│   └── services/
│       └── ai_service.py               # OpenAI integration, prompt engine
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## API Endpoints

| Method | Endpoint                      | Auth | Description                      |
| ------ | ----------------------------- | ---- | -------------------------------- |
| POST   | `/api/v1/auth/register`       | No   | Register new user                |
| POST   | `/api/v1/auth/login`          | No   | Login, receive JWT               |
| GET    | `/api/v1/auth/me`             | Yes  | Get current user                 |
| GET    | `/api/v1/ideas`               | Yes  | List user's ideas                |
| POST   | `/api/v1/ideas`               | Yes  | Create new idea thread           |
| GET    | `/api/v1/ideas/{id}`          | Yes  | Get idea details                 |
| PATCH  | `/api/v1/ideas/{id}`          | Yes  | Update idea                      |
| DELETE | `/api/v1/ideas/{id}`          | Yes  | Delete idea                      |
| GET    | `/api/v1/ideas/{id}/messages` | Yes  | Get conversation history         |
| POST   | `/api/v1/ideas/{id}/messages` | Yes  | Send message, stream AI response |
| GET    | `/health`                     | No   | Health check                     |

---

## Running Locally

```bash
# Clone the repository
git clone https://github.com/CynthiaKaluson/cerebro-api.git
cd cerebro-api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your real values

# Start PostgreSQL
docker compose up -d db

# Run the API
uvicorn app.main:app --reload
```

API runs at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## Testing the Streaming Endpoint

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword", "full_name": "Your Name"}'

# 2. Login and copy the access_token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# 3. Create an idea
curl -X POST "http://localhost:8000/api/v1/ideas" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Idea", "description": "A brief description of your idea"}'

# 4. Stream a conversation (watch tokens arrive in real time)
curl -X POST "http://localhost:8000/api/v1/ideas/YOUR_IDEA_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "I think this will work because..."}' \
  --no-buffer
```

---

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini
```

---

## Author

**Cynthia Kalu Okorie**

Backend developer focused on AI systems, async APIs, and production-grade
backend engineering.
