# Backend Setup Guide

## ✅ Backend Pulled from GitHub

The backend has been pulled from `https://github.com/dzhou6/SPEED.git` and is ready to use.

## Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app with all endpoints
│   ├── models.py        # Pydantic request/response models
│   ├── db.py            # MongoDB connection (Motor async)
│   ├── config.py        # Environment config
│   ├── matching.py      # Ranking algorithm
│   └── seed_demo.py     # Demo data seeding
├── Dockerfile           # Container setup
└── requirements.txt    # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

Create `backend/.env` file:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=coursecupid
```

**Get MongoDB Atlas:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create cluster (free tier)
4. Create database user
5. Whitelist IP (0.0.0.0/0 for dev)
6. Get connection string → paste in `.env`

### 3. Seed Demo Data

```bash
cd backend
python -m app.seed_demo
```

This creates:
- Course: CS471
- 3 demo users (Ava, Noah, Mia)
- Course materials and syllabus

### 4. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Or:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 5. Test

- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

## API Endpoints

All endpoints require `X-User-Id` header (except `/auth/demo`):

- `POST /auth/demo` - Create demo user
- `POST /profile` - Update profile (requires X-User-Id)
- `GET /recommendations?courseCode=X` - Get matches (requires X-User-Id)
- `POST /swipe` - Accept/pass (requires X-User-Id)
- `GET /pod?courseCode=X` - Get pod (requires X-User-Id)
- `POST /pod/hub` - Set Pod Hub link (requires X-User-Id)
- `POST /heartbeat?courseCode=X` - Update presence (requires X-User-Id)
- `POST /ask` - 3-layer help system (requires X-User-Id)
- `GET /health` - Health check

## Frontend Connection

Frontend is already configured to:
- Send `X-User-Id` header automatically
- Handle backend response format (`rolePrefs`, `lastActiveAt`, etc.)
- Work with ObjectId user IDs

Set frontend environment:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 3-Layer Help System

Currently implemented as simplified version:
- **Layer 1**: Returns syllabus text snippet
- **Layer 2**: Returns relevant material links based on keywords
- **Layer 3**: Creates ticket in database

**To add PatriotAI:**
1. Add `OPENAI_API_KEY` to `.env`
2. Update `app/main.py` `/ask` endpoint to call PatriotAI API
3. Use syllabus text and materials from database

## Docker (Optional)

```bash
cd backend
docker build -t coursecupid-backend .
docker run -p 8000:8000 --env-file .env coursecupid-backend
```

## Troubleshooting

**MongoDB connection fails:**
- Check `.env` file exists
- Verify MONGO_URI is correct
- Check IP whitelist in Atlas
- Ensure database user has read/write permissions

**Frontend can't connect:**
- Check backend is running on port 8000
- Verify CORS is enabled (already configured)
- Check `VITE_API_BASE_URL` in frontend

**No recommendations:**
- Run seed script: `python -m app.seed_demo`
- Check users are in same courseCode
- Verify userId is valid ObjectId
