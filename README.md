# OPD Claim Adjudication MVP

A production-grade claim adjudication system for "Plum OPD Advantage" health insurance policy. Built with **Flask + PostgreSQL** backend and **Next.js** frontend.

## Features

- ✅ Deterministic rule-based claim adjudication engine
- ✅ PostgreSQL database for claims, members, and documents
- ✅ REST API with comprehensive validation (Flask + Pydantic)
- ✅ 10 automated test cases covering all scenarios (TC001-TC010)
- ✅ Network hospital cashless approvals
- ✅ Pre-authorization requirements for diagnostics
- ✅ Waiting period enforcement (30 days initial, 90 days for specific conditions)
- ✅ Partial approvals for mixed coverage scenarios
- ✅ Fraud detection and manual review flagging
- ✅ Confidence scoring for all decisions
- ✅ Docker Compose for local development

## Architecture

```
┌─────────────────────────────────────────┐
│         Next.js Frontend (3000)          │
│  (Claim form, status tracking, test UI)  │
└────────────────┬────────────────────────┘
                 │ HTTP/REST
┌─────────────────▼────────────────────────┐
│       Flask API (8000)                   │
│  ├─ POST /claims                         │
│  ├─ POST /adjudicate                     │
│  ├─ GET /claims/{id}                     │
│  ├─ GET /members                         │
│  ├─ GET /health                          │
│  └─ SQLAlchemy ORM Models                │
└────────────────┬────────────────────────┘
                 │ SQLAlchemy
┌─────────────────▼────────────────────────┐
│    PostgreSQL Database (5432)             │
│  ├─ members                              │
│  ├─ claims                               │
│  ├─ line_items                           │
│  ├─ documents                            │
│  └─ prescriptions                        │
└──────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OR Python 3.11+ & Node.js 18+ (for local development)
- PostgreSQL 15+ (if running locally without Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Build images
make docker-build

# Start services
make docker-up

# View logs
make docker-logs

# Run tests
make test

# Stop services
make docker-down
```

**Services:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- Database: postgres://opd_user:opd_password@localhost:5432/opd_claim

### Option 2: Local Development

#### Backend Setup

```bash
cd apps/api

# Install dependencies
pip install -r requirements.txt

# Create .env file with PostgreSQL connection
cat > .env << EOF
FLASK_ENV=development
FLASK_APP=wsgi.py
DATABASE_URL=postgresql://user:password@localhost:5432/opd_claim
API_KEY=local-dev
EOF

# Run migrations
flask db upgrade

# Start Flask server
python wsgi.py
```

Server runs on `http://localhost:8000`

#### Frontend Setup

```bash
cd apps/web

npm install
npm run dev
```

App runs on `http://localhost:3000`

## Testing

### Run All Tests

```bash
make test
```

### Run Specific Test Case

```bash
cd apps/api
pytest tests/test_adjudication.py::TestTC001SimpleConsultation -v
```

### Test Cases Implemented

| Test ID | Scenario | Expected Decision |
|---------|----------|-------------------|
| TC001 | Simple Consultation | APPROVED (₹1350, 10% copay) |
| TC002 | Dental Treatment with cosmetic | PARTIAL (₹8000, cosmetic excluded) |
| TC003 | Claim exceeds ₹5000 limit | REJECTED |
| TC004 | Missing prescription | REJECTED |
| TC005 | Type 2 Diabetes (90-day waiting) | REJECTED |
| TC006 | MRI without pre-auth | REJECTED |
| TC007 | Multiple high-value same-day claims | MANUAL_REVIEW |
| TC008 | Weight loss treatment (excluded) | REJECTED |
| TC009 | Network hospital cashless | APPROVED + cashless_approved |
| TC010 | (Bonus) Additional scenario | Testing framework in place |

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "OPD Claim Adjudication API",
  "version": "1.0.0"
}
```

### Adjudicate Claim

```bash
POST /adjudicate
X-API-Key: local-dev
Content-Type: application/json

{
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
    },
    {
      "type": "diagnostic",
      "description": "CBC + Dengue test",
      "amount": 500
    }
  ],
  "prescription": {
    "doctor_name": "Dr. Sharma",
    "doctor_reg": "KA/45678/2015",
    "diagnosis": "Viral fever",
    "tests": ["CBC", "Dengue"],
    "valid": true
  }
}
```

Response:
```json
{
  "claim_id": "CLM_ABC12345",
  "decision": "APPROVED",
  "approved_amount": 1350,
  "deductions": {
    "copay": 150
  },
  "cashless_approved": false,
  "notes": "Claim approved after verification",
  "confidence_score": 0.95
}
```

### Create Claim & Save to DB

```bash
POST /claims
X-API-Key: local-dev
Content-Type: application/json

# Same payload as /adjudicate
```

### Get Member

```bash
GET /members/{member_id}
X-API-Key: local-dev
```

### List Members

```bash
GET /members
X-API-Key: local-dev
```

### Get Claim

```bash
GET /claims/{claim_id}
X-API-Key: local-dev
```

## Configuration

### Policy Terms

Policy configuration is loaded from `packages/shared/policy_terms.json`:

```json
{
  "limits": {
    "annual_limit": 50000,
    "per_claim_limit": 5000
  },
  "coverage": {
    "consultation": {
      "sub_limit": 2000,
      "copay_percentage": 10,
      "network_discount_percentage": 20
    },
    "diagnostics": {
      "sub_limit": 10000,
      "copay_percentage": 0,
      "requires_pre_auth_list": ["MRI", "CT"],
      "pre_auth_required_threshold": 10000
    },
    ...
  },
  "waiting_periods": {
    "initial_waiting_days": 30,
    "specific_ailments": {
      "diabetes": 90,
      "hypertension": 90,
      "ped": 365
    }
  },
  "exclusions": [
    "cosmetic procedures",
    "weight loss",
    "bariatric"
  ]
}
```

### Environment Variables

```env
FLASK_ENV=development|production
DATABASE_URL=postgresql://user:password@host:5432/dbname
API_KEY=your-secret-key
```

## Database Schema

### Members Table
```sql
CREATE TABLE members (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  join_date TIMESTAMP NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now()
);
```

### Claims Table
```sql
CREATE TABLE claims (
  id VARCHAR(50) PRIMARY KEY,
  member_id VARCHAR(50) REFERENCES members(id),
  treatment_date TIMESTAMP NOT NULL,
  hospital VARCHAR(255),
  is_network BOOLEAN DEFAULT false,
  cashless_requested BOOLEAN DEFAULT false,
  status VARCHAR(50),
  decision_json JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

## Deployment

### Vercel (Frontend)

1. Push code to GitHub
2. Connect repo to Vercel
3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.example.com
   ```
4. Deploy with `vercel deploy`

### Render/Railway (Backend)

1. Create PostgreSQL database
2. Deploy Flask app from GitHub
3. Set environment variables:
   ```
   DATABASE_URL=postgresql://...
   API_KEY=your-secret-key
   FLASK_ENV=production
   ```
4. Set start command: `gunicorn wsgi:app`

## Project Structure

```
.
├── apps/
│   ├── api/                    # Flask backend
│   │   ├── app/
│   │   │   ├── main.py         # Flask app + routes
│   │   │   ├── config.py       # Configuration
│   │   │   ├── db_models.py    # SQLAlchemy models
│   │   │   ├── schemas.py      # Pydantic schemas
│   │   │   └── rules/
│   │   │       └── engine.py   # Adjudication logic
│   │   ├── tests/
│   │   │   ├── test_adjudication.py  # All 10 test cases
│   │   │   └── conftest.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── wsgi.py             # WSGI entry point
│   │   └── pytest.ini
│   └── web/                    # Next.js frontend
│       ├── app/
│       ├── components/
│       ├── package.json
│       └── next.config.js
├── packages/
│   └── shared/
│       ├── policy_terms.json   # Policy configuration
│       └── test_cases.json     # Test data
├── docker-compose.yml
├── Makefile
└── README.md
```

## Key Rules Implemented

### Adjudication Decision Flow

1. **Basic Eligibility Check**
   - Member exists and is active
   - Waiting period satisfied (initial 30 days, specific ailments up to 365 days)

2. **Document Validation**
   - Prescription required and valid
   - Doctor registration format: `{STATE}/{NUMBER}/{YEAR}` (e.g., `KA/45678/2015`)

3. **Coverage Verification**
   - Service is covered (not in exclusion list)
   - Sub-limits checked
   - Pre-authorization required for certain tests (MRI, CT) when > ₹10,000

4. **Fraud Detection**
   - Multiple high-value claims same day → MANUAL_REVIEW
   - Unusual patterns flagged

5. **Limits & Copays Calculation**
   - Annual limit: ₹50,000
   - Per-claim limit: ₹5,000 (hard cap)
   - Network discount: 20% (applied before copay)
   - Co-pays:
     - Consultation: 10%
     - Pharmacy: 30% (for branded)
     - Alternative: varies by type

6. **Decision Output**
   ```json
   {
     "decision": "APPROVED|REJECTED|PARTIAL|MANUAL_REVIEW",
     "approved_amount": number,
     "rejection_reasons": ["REASON_CODE"],
     "deductions": { "copay": number, "network_discount": number },
     "confidence_score": 0.0-1.0,
     "notes": "Human-readable explanation"
   }
   ```

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if DB is running
docker ps | grep postgres

# Recreate database
docker-compose down -v
docker-compose up db -d
```

### Tests Failing
```bash
# Check logs
make docker-logs-api

# Run single test with verbose output
cd apps/api
pytest tests/test_adjudication.py::TestTC001SimpleConsultation -vvs
```

### Frontend Not Connecting to API
```bash
# Check NEXT_PUBLIC_API_URL in .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > apps/web/.env.local

# Restart frontend
cd apps/web && npm run dev
```

## Future Enhancements

- [ ] Real OCR integration (Google Cloud Vision, AWS Textract)
- [ ] LLM-based document extraction confidence scoring
- [ ] Analytics dashboard
- [ ] Email notifications for claim status
- [ ] Bulk claim import/export (CSV)
- [ ] Advanced fraud detection (ML models)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Audit logging
- [ ] Single sign-on (OAuth 2.0)

## API Documentation

Auto-generated API docs available at (when using FastAPI):
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

For Flask, consider adding `flask-restx` or `flasgger` for Swagger docs.

## Support

For issues, questions, or feature requests, open an issue on GitHub or contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** June 2024  
**License:** Proprietary
