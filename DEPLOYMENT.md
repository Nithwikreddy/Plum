# Deployment Guide for OPD Claim Adjudication MVP

## Frontend Deployment (Next.js → Vercel)

### Prerequisites
- Vercel account (free at vercel.com)
- GitHub repository with your code

### Steps

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/opd-claim-adjudication.git
   git push -u origin main
   ```

2. **Create Vercel Project**
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your GitHub repo
   - Choose "Next.js" framework (auto-detected)

3. **Configure Root Directory**
   - Root Directory: `apps/web`
   - Click Deploy

4. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-api-domain.com
     ```

5. **Deploy**
   - Click Deploy
   - Wait for deployment to complete
   - Your frontend is now live at `your-project.vercel.app`

### Production Optimizations

In `apps/web/next.config.js`:
```javascript
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true, // for static export if needed
  },
}
```

---

## Backend Deployment (Flask → Railway/Render)

### Option A: Railway (Recommended for beginners)

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select repo

3. **Add PostgreSQL Database**
   - Click "Add a Service"
   - Select "PostgreSQL"
   - Railway automatically creates the database

4. **Configure Flask Service**
   - Click "Deploy" on your repo
   - Set Root Directory: `apps/api`
   - In Variables tab, add:
     ```
     FLASK_ENV=production
     DATABASE_URL=<auto-filled by PostgreSQL service>
     API_KEY=your-secret-key-here
     PYTHON_VERSION=3.11
     ```
   - Set Start Command:
     ```
     gunicorn wsgi:app
     ```

5. **Deploy**
   - Railway automatically deploys
   - Your API is live at `your-project.railway.app`

### Option B: Render.com

1. **Create Render Account**
   - Go to https://render.com
   - Sign up

2. **Create PostgreSQL Database**
   - Click "New +"
   - Select "PostgreSQL"
   - Name: `opd-claim-db`
   - Note the connection string

3. **Create Flask Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app --workers 4 --bind 0.0.0.0:8000`
   - Root Directory: `apps/api`
   - Instance Type: Free (starter)

4. **Set Environment Variables**
   - In Environment tab:
     ```
     FLASK_ENV=production
     DATABASE_URL=<from PostgreSQL service>
     API_KEY=your-secret-key-here
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Render deploys automatically
   - Your API is at `your-project.onrender.com`

### Option C: Heroku (Legacy, slower free tier)

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-opd-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set API_KEY=your-secret-key

# Deploy
git push heroku main

# View logs
heroku logs -t
```

---

## Backend + Frontend Together (Docker)

### AWS ECS / Google Cloud Run

1. **Build and Push Docker Images**
   ```bash
   docker build -t opd-api apps/api
   docker build -t opd-web apps/web
   
   # Push to Docker Hub / ECR
   docker tag opd-api yourusername/opd-api:latest
   docker push yourusername/opd-api:latest
   ```

2. **Deploy with Docker Compose on Cloud**
   - Use AWS Lightsail or Google Cloud Run
   - Deploy docker-compose.yml with PostgreSQL

---

## Environment Variables Summary

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://api.yourcompany.com
```

### Backend (Flask)
```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/opd_claim
API_KEY=strong-secret-key-min-32-chars
PYTHONUNBUFFERED=1
```

---

## Database Migrations in Production

After deployment:

```bash
# Via Railway/Render terminal (if available)
flask db upgrade

# OR run migration on first boot by adding to wsgi.py:
import os
from app.main import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'production'))

# Auto-migrate on startup
with app.app_context():
    db.create_all()
```

---

## Monitoring & Logs

### Railway
- Dashboard shows logs automatically
- Click "Logs" tab

### Render
- Click "Logs" tab in dashboard
- Set up email alerts in settings

### Vercel
- Deployment logs shown in dashboard
- Runtime errors in Functions tab

---

## Custom Domain Setup

### Vercel (Frontend)
1. Go to Project Settings → Domains
2. Add your domain (e.g., claims.yourcompany.com)
3. Update DNS records per Vercel instructions

### Railway/Render (Backend)
1. Add custom domain in service settings
2. Update DNS to point to service URL
3. Configure CORS in Flask to allow your frontend domain:

```python
# In app/main.py
CORS_ORIGINS = [
    "https://claims.yourcompany.com",
    "https://www.yourcompany.com"
]
```

---

## SSL/HTTPS

- **Vercel**: Automatic (free)
- **Railway/Render**: Automatic (free)
- **Custom domain**: Use Route 53 / CloudFlare

---

## Cost Estimate (Monthly)

| Service | Free Tier | Paid (Starting) |
|---------|-----------|-----------------|
| Vercel (Frontend) | ✅ Unlimited | $20 |
| Railway (Backend) | ✅ $5/month | $0.50/GB+compute |
| Render (Backend) | ✅ Limited | $7/month |
| PostgreSQL (Railway) | ✅ $5/month | Variable |

**Recommended:** Railway free tier covers both frontend + backend + DB for first month.

---

## Rollback Procedure

### Vercel
- Click "Deployments" → select previous version → "Redeploy"

### Railway
- Click "Deployments" → select previous → "Redeploy"

### Manual Rollback
```bash
git revert <commit-hash>
git push origin main
# Auto-redeploy triggered
```

---

## Performance Tips

1. **Enable Caching**
   - Vercel: Auto (ISR, edge cache)
   - Railway: Add Redis cache layer

2. **Database Indexing**
   ```sql
   CREATE INDEX idx_member_id ON claims(member_id);
   CREATE INDEX idx_status ON claims(status);
   ```

3. **API Rate Limiting**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-Key'))
   
   @app.route('/adjudicate', methods=['POST'])
   @limiter.limit("100 per hour")
   def adjudicate():
       ...
   ```

4. **Connection Pooling**
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_size': 10,
       'pool_recycle': 3600,
   }
   ```

---

## Production Checklist

- [ ] Database backups enabled
- [ ] Environment variables set (not hardcoded)
- [ ] CORS configured for allowed domains
- [ ] API key rotated and secured
- [ ] Logs monitored
- [ ] Error tracking (Sentry) configured
- [ ] Database indexed
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Health check endpoint monitored

---

For support, see README.md or contact devops@yourcompany.com
