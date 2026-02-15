# CourseCupid MVP

A course collaboration platform that helps students find study partners and project teammates, get help quickly, and build a shared "Study Hub" for notes, links, and tasks. 💘📚

## 🚀 Quick Start (2-Minute Demo)

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- MongoDB Atlas account (free tier) or local MongoDB

### Setup Steps

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/dzhou6/SPEED.git
   cd SPEED
   ```

2. **Set up environment:**
   ```bash
   # Windows
   .\scripts\setup_env.ps1
   
   # Or manually: copy .env.example to .env and fill in MONGO_URI
   ```

3. **Edit `.env` file:**
   - Get MongoDB Atlas connection string from https://www.mongodb.com/cloud/atlas
   - Paste into `MONGO_URI=`
   - (Optional) Set `VITE_API_BASE_URL=http://localhost:8000`

4. **Seed demo data:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m app.seed_demo
   ```

5. **Run the application:**
   
   **Option A: Docker (Recommended)**
   ```bash
   make up
   # Or: docker-compose up --build
   ```
   
   **Option B: Manual**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   npm install
   npm run dev
   ```

6. **Open browser:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

## 📋 Demo Script (2 Minutes)

1. **Join Course:**
   - Open http://localhost:5173
   - Enter course code: `CS471`
   - Click "Join"
   - ✅ You get a userId

2. **Build Profile:**
   - Select 1-2 roles (Frontend, Backend, Matching, Platform)
   - Add skills tags
   - Set availability
   - Click "Save profile"
   - ✅ Redirected to Match Feed

3. **View Matches:**
   - See 12 demo users with different roles
   - Each shows: roles, skills, availability, last active
   - "Why this match" reasons displayed
   - ✅ Match feed populated

4. **Accept Matches:**
   - Click "Accept" on 2-3 users
   - When mutual accept happens → pod forms
   - ✅ Auto-redirected to Pod Page

5. **Pod Features:**
   - See pod members
   - Contact cards unlock after mutual accept
   - Leader can set Pod Hub link (Google Doc/Sheet)
   - ✅ Pod coordination ready

6. **3-Layer Help System:**
   - Click "Ask for Help"
   - Try: "When is the final exam?" → Layer 1 (Logistics)
   - Try: "Explain system design" → Layer 2 (Pointer to materials)
   - Try: "Help with homework" → Layer 3 (Escalation ticket)
   - ✅ All 3 layers working

## 🏗️ Project Structure

```
SPEED/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py    # API endpoints
│   │   ├── db.py      # MongoDB connection
│   │   ├── seed_demo.py  # Demo data seeding
│   │   └── ...
│   └── requirements.txt
├── src/               # React frontend
│   ├── pages/        # Join, Profile, MatchFeed, PodPage
│   └── api/          # API client
├── scripts/          # Setup scripts
├── docker-compose.yml
└── Makefile
```

## 🔧 Configuration

### MongoDB Atlas Setup

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account → Create cluster (free tier M0)
3. **Database Access:**
   - Create database user
   - Save username/password
4. **Network Access:**
   - Click "Add IP Address"
   - For development: Use `0.0.0.0/0` (allow all IPs)
   - For production: Add specific IPs
5. **Get Connection String:**
   - Click "Connect" → "Connect your application"
   - Copy connection string
   - Replace `<password>` with your database user password
   - Paste into `.env` as `MONGO_URI`

### Environment Variables

See `.env.example` for all required variables:
- `MONGO_URI` - MongoDB connection string (required)
- `MONGO_DB` - Database name (default: coursecupid)
- `VITE_API_BASE_URL` - Backend URL (default: http://localhost:8000)

## 📦 Available Commands

### Using Makefile
```bash
make up        # Start backend + frontend with Docker
make down      # Stop containers
make seed      # Seed demo data
make logs      # View logs
make reset     # Reset everything (removes volumes)
```

### Manual Commands
```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
npm run dev

# Seed data
cd backend
python -m app.seed_demo
```

## 🧪 Testing the Demo

After seeding, you should see:
- ✅ 12 demo users in match feed
- ✅ Course CS471 with syllabus
- ✅ 12 materials for Layer 2 AI
- ✅ Varied activity timestamps

## 🐛 Troubleshooting

**Backend won't start:**
- Check `.env` file exists and has `MONGO_URI`
- Verify MongoDB Atlas IP allowlist includes your IP
- Check backend logs: `docker-compose logs backend`

**Frontend can't connect:**
- Verify backend is running: http://localhost:8000/health
- Check `VITE_API_BASE_URL` in `.env`
- Check browser console for CORS errors

**No matches appear:**
- Run seed script: `python -m app.seed_demo`
- Check MongoDB connection
- Verify users are in same courseCode

**Database connection errors:**
- Check MONGO_URI format (no quotes around value)
- Verify IP is whitelisted in Atlas
- Check database user permissions

## 📚 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 🎯 MVP Features

- ✅ Course joining
- ✅ Profile building
- ✅ Match recommendations (role-balanced)
- ✅ Swipe/accept system
- ✅ Pod formation (mutual accept)
- ✅ Pod Hub link management
- ✅ 3-layer help system (Logistics, Pointer, Escalation)
- ✅ Activity tracking (heartbeat)
- ✅ Demo data seeding

## 🚢 Deployment (Optional)

**Backend:**
- Render/Railway: Deploy `backend/` folder
- Set `MONGO_URI` environment variable
- Expose port 8000

**Frontend:**
- Vercel/Netlify: Deploy `src/` folder
- Set `VITE_API_BASE_URL` to backend URL
- Build command: `npm run build`

## 📝 License

MIT
