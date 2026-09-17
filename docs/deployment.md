# Deployment & Production Guide

## Running Locally

### 1. Backend

```bash
cd backend
uv venv .venv --python 3.12
uv pip install -r requirements.txt --python .venv/Scripts/python.exe
.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Running with Docker Compose

```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API & OpenAPI docs: `http://localhost:8000/docs`
