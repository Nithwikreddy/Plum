# Setup & Installation Guide

## Prerequisites

### For Docker (Recommended)
- Docker Desktop (Windows, Mac, Linux)
  - Download: https://www.docker.com/products/docker-desktop
  - Includes Docker and Docker Compose
  - 4GB RAM minimum, 10GB disk space

### For Local Development
- **Python 3.11+**
  - Download: https://python.org
  - Windows: Add to PATH during installation
  - Verify: `python --version`

- **Node.js 18+**
  - Download: https://nodejs.org
  - Choose LTS version
  - Verify: `node --version` and `npm --version`

- **PostgreSQL 15+**
  - Download: https://postgresql.org
  - Note database connection string
  - Windows: Add to PATH if needed

- **Git** (optional, for version control)
  - Download: https://git-scm.com

---

## Option 1: Docker Compose (Easiest)

### Step 1: Quick Start

**Windows:**
```bash
# Double-click quickstart.bat
# OR from command prompt:
quickstart.bat
```

**Mac/Linux:**
```bash
# Make executable
chmod +x quickstart.sh

# Run
./quickstart.sh
```

This will:
- Build Docker images
- Start PostgreSQL, Flask API, and Next.js
- Run health checks
- Open http://localhost:3000 in browser

### Step 2: Verify Services

Check all services are running:
```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                  SERVICE   STATUS
opd_api             flask run --host=0...    api       Up
opd_db              postgres                 db        Up
opd_web             npm start                web       Up
```

### Step 3: Access Services

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Database**: `localhost:5432` (user: `opd_user`, password: `opd_password`)

### Step 4: Run Tests

```bash
# Run all tests
docker-compose exec api pytest tests/ -v

# Run specific test
docker-compose exec api pytest tests/test_adjudication.py::TestTC001SimpleConsultation -v
```

### Step 5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean database)
docker-compose down -v
```

---

## Option 2: Local Development

### Step 1: Clone or Navigate to Project

```bash
cd "c:\Users\Nithwik reddy\OneDrive\Desktop\New folder (2)"
```

### Step 2: Backend Setup

#### Create Virtual Environment

**Windows:**
```bash
cd apps\api

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Verify prompt shows (venv)
```

**Mac/Linux:**
```bash
cd apps/api

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify prompt shows (venv)
```

#### Install Dependencies

```bash
# Ensure venv is activated
pip install --upgrade pip

pip install -r requirements.txt

# Verify installation
python -c "import flask; print(flask.__version__)"
```

#### Configure Environment

Create `.env` file:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Edit `.env`:
```env
FLASK_ENV=development
FLASK_APP=wsgi.py
DATABASE_URL=postgresql://postgres:password@localhost:5432/opd_claim
API_KEY=local-dev
```

#### Setup Database

**Option A: Using Local PostgreSQL**

1. Install PostgreSQL from https://postgresql.org

2. Create database:
   ```bash
   psql -U postgres
   # In psql prompt:
   CREATE DATABASE opd_claim;
   CREATE USER opd_user WITH PASSWORD 'opd_password';
   GRANT ALL PRIVILEGES ON DATABASE opd_claim TO opd_user;
   \q
   ```

3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://opd_user:opd_password@localhost:5432/opd_claim
   ```

**Option B: Using Docker PostgreSQL (without full Docker Compose)**

```bash
# Start only database
docker run -d \
  --name opd_postgres \
  -e POSTGRES_DB=opd_claim \
  -e POSTGRES_USER=opd_user \
  -e POSTGRES_PASSWORD=opd_password \
  -p 5432:5432 \
  postgres:15-alpine

# Verify
docker ps | grep opd_postgres
```

#### Initialize Database

```bash
# From apps/api directory with venv activated
python init_db.py
```

Output:
```
Creating database tables...
Seeding test members...
  Added member: EMP001 (Ramesh Kumar)
  Added member: EMP002 (Priya Singh)
  ...
Database initialization complete!
Total members: 9
```

#### Start Flask Server

```bash
# From apps/api directory with venv activated
python wsgi.py
```

Output:
```
 * Serving Flask app 'wsgi'
 * Debug mode: on
 * Running on http://127.0.0.1:8000
```

API is now at: **http://localhost:8000**

**Stop:** Press `Ctrl+C`

### Step 3: Frontend Setup

In a **new terminal**, navigate to web directory:

```bash
cd apps/web

# Install dependencies
npm install

# Verify
npm --version  # Should be 9+
```

### Step 4: Start Frontend

```bash
# From apps/web directory
npm run dev
```

Output:
```
  ▲ Next.js 14.0.0
  - Local:        http://localhost:3000
```

Frontend is now at: **http://localhost:3000**

**Stop:** Press `Ctrl+C`

### Step 5: Run Tests

In a **third terminal**, run tests:

```bash
cd apps/api

# Activate venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_adjudication.py::TestTC001SimpleConsultation -v
```

### Step 6: Deactivate Virtual Environment

When done:
```bash
deactivate
```

---

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000

# Kill process (example PID 1234)
# Windows
taskkill /PID 1234 /F

# Mac/Linux
kill -9 1234
```

### Issue: Database Connection Failed

```bash
# Test PostgreSQL connection
psql -U opd_user -d opd_claim -h localhost

# Or with Python
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://opd_user:opd_password@localhost:5432/opd_claim'); print(engine.connect())"
```

### Issue: Python Not Found

```bash
# Verify Python installation
python --version
# or
python3 --version

# If not found, add to PATH or use full path
C:\Python311\python.exe --version
```

### Issue: npm: command not found

```bash
# Verify Node.js installation
node --version
npm --version

# If not found, reinstall from nodejs.org
```

### Issue: Docker Permission Denied

**Windows:**
- Ensure Docker Desktop is running
- Run terminal as Administrator

**Mac/Linux:**
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply new group membership (logout and login, or:)
newgrp docker
```

### Issue: API Not Connecting to Frontend

1. Check CORS configuration in `apps/api/app/main.py`
2. Verify API is running on port 8000
3. Check browser console for errors
4. Update frontend API URL if needed

### Issue: Tests Failing

```bash
# Run with verbose output
pytest tests/ -vvs

# Check logs
docker-compose logs api  # if using Docker

# Check database
psql -U opd_user -d opd_claim -c "SELECT * FROM members;"
```

---

## Using Make Commands (if Make is installed)

```bash
# Install dependencies
make install

# Start development servers
make dev

# Run tests
make test

# Seed database
make seed

# Docker operations
make docker-build
make docker-up
make docker-down
make docker-logs
```

---

## First Test Claim

After starting services, test an adjudication:

```bash
# Using curl
curl -X POST http://localhost:8000/adjudicate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local-dev" \
  -d '{
    "member_id": "EMP001",
    "treatment_date": "2024-09-15",
    "hospital": "Apollo",
    "is_network": true,
    "cashless_requested": false,
    "line_items": [
      {
        "type": "consultation",
        "description": "Viral fever consultation",
        "amount": 1000
      }
    ],
    "prescription": {
      "doctor_name": "Dr. Sharma",
      "doctor_reg": "KA/45678/2015",
      "diagnosis": "Viral fever",
      "valid": true
    }
  }'
```

Expected response:
```json
{
  "claim_id": "CLM_ABC12345",
  "decision": "APPROVED",
  "approved_amount": 900,
  "deductions": {
    "copay": 100
  },
  "confidence_score": 0.95,
  "notes": "Claim approved after verification"
}
```

---

## Environment Variables Reference

### Backend (.env)
```env
# Flask Configuration
FLASK_ENV=development          # development, testing, production
FLASK_APP=wsgi.py            # WSGI application file

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Security
API_KEY=local-dev             # Change in production

# Optional
DEBUG=true                    # Enables debug mode
PYTHONUNBUFFERED=1           # Unbuffered output
```

### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_ENV=development
```

---

## Next Steps

1. ✅ Services running
2. ✅ Tests passing
3. Next:
   - Review API documentation
   - Test via UI at http://localhost:3000
   - Run all 10 test cases
   - Check deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

---

For additional help, see [README.md](README.md) or contact support.
