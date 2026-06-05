import pytest
import json
from pathlib import Path
from datetime import datetime
from app.main import create_app
from app.db_models import db

# Create app for testing
@pytest.fixture
def app():
    """Create app instance for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()


class TestTC001SimpleConsultation:
    """TC001: Simple Consultation - Approved"""
    
    def test_tc001_simple_consultation_approved(self, client):
        request_payload = {
            "member_id": "EMP001",
            "treatment_date": "2024-09-15",
            "hospital": "Apollo",
            "is_network": True,
            "cashless_requested": False,
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
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "APPROVED"
        assert result["approved_amount"] == 1350
        assert result["deductions"]["copay"] == 150
        assert result["confidence_score"] == 0.95


class TestTC002DentalTreatment:
    """TC002: Dental Treatment - Partial Approval"""
    
    def test_tc002_dental_treatment_partial_approval(self, client):
        request_payload = {
            "member_id": "EMP002",
            "treatment_date": "2024-09-16",
            "hospital": "Max",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "dental",
                    "description": "Root canal",
                    "amount": 8000
                },
                {
                    "type": "dental",
                    "description": "Teeth whitening",
                    "amount": 4000
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Patel",
                "doctor_reg": "GJ/12345/2018",
                "diagnosis": "Dental caries",
                "procedures": ["Root canal", "Teeth whitening"],
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "PARTIAL"
        assert result["approved_amount"] == 8000
        assert "Teeth whitening - cosmetic procedure" in result["rejected_items"]
        assert result["confidence_score"] == 0.92


class TestTC003LimitExceeded:
    """TC003: Limit Exceeded - Rejected"""
    
    def test_tc003_limit_exceeded_rejected(self, client):
        request_payload = {
            "member_id": "EMP003",
            "treatment_date": "2024-09-17",
            "hospital": "Fortis",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "General consultation",
                    "amount": 2000
                },
                {
                    "type": "pharmacy",
                    "description": "Medications",
                    "amount": 5500
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Kumar",
                "doctor_reg": "KA/98765/2020",
                "diagnosis": "Hypertension",
                "medicines": ["Amlodipine"],
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "REJECTED"
        assert "PER_CLAIM_EXCEEDED" in result["rejection_reasons"]
        assert result["notes"] == "Claim amount exceeds per-claim limit of ₹5000"
        assert result["confidence_score"] == 0.98


class TestTC004MissingDocuments:
    """TC004: Missing Documents - Rejected"""
    
    def test_tc004_missing_documents_rejected(self, client):
        request_payload = {
            "member_id": "EMP004",
            "treatment_date": "2024-09-18",
            "hospital": "Manipal",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "General consultation",
                    "amount": 1500
                }
            ],
            "prescription": None
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "REJECTED"
        assert "MISSING_DOCUMENTS" in result["rejection_reasons"]
        assert result["notes"] == "Prescription from registered doctor is required"
        assert result["confidence_score"] == 1.0


class TestTC005WaitingPeriod:
    """TC005: Pre-existing Condition - Waiting Period"""
    
    def test_tc005_waiting_period_rejected(self, client):
        request_payload = {
            "member_id": "EMP005",
            "member_join_date": "2024-09-01",
            "treatment_date": "2024-10-15",
            "hospital": "Narayana",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "Diabetes consultation",
                    "amount": 1500
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Singh",
                "doctor_reg": "PB/55555/2019",
                "diagnosis": "Type 2 Diabetes",
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "REJECTED"
        assert "WAITING_PERIOD" in result["rejection_reasons"]
        assert "90-day waiting period" in result["notes"]
        assert "2024-11-30" in result["notes"]
        assert result["confidence_score"] == 0.96


class TestTC006PreAuthRequired:
    """TC006: Diagnostic Tests - Pre-auth Required"""
    
    def test_tc006_preauth_required_rejected(self, client):
        request_payload = {
            "member_id": "EMP006",
            "treatment_date": "2024-09-19",
            "hospital": "Apollo",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "diagnostic",
                    "description": "MRI Lumbar Spine",
                    "amount": 15000
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Desai",
                "doctor_reg": "MH/77777/2017",
                "diagnosis": "Lower back pain",
                "tests": ["MRI Lumbar Spine"],
                "valid": True
            },
            "pre_auth_id": None
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "REJECTED"
        assert "PRE_AUTH_MISSING" in result["rejection_reasons"]
        assert "MRI requires pre-authorization" in result["notes"]
        assert result["confidence_score"] == 0.94


class TestTC007FraudDetection:
    """TC007: Fraud Detection - Manual Review"""
    
    def test_tc007_fraud_detection_manual_review(self, client):
        request_payload = {
            "member_id": "EMP007",
            "treatment_date": "2024-09-20",
            "hospital": "Max",
            "is_network": True,
            "cashless_requested": False,
            "previous_claims_same_day": 3,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "Multiple consultation",
                    "amount": 3000
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Verma",
                "doctor_reg": "DL/11111/2021",
                "diagnosis": "Routine checkup",
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "MANUAL_REVIEW"
        assert "Multiple claims same day" in result["flags"]
        assert "Unusual pattern detected" in result["flags"]
        assert result["confidence_score"] == 0.65


class TestTC008ExcludedTreatment:
    """TC008: Excluded Treatment - Rejected"""
    
    def test_tc008_excluded_treatment_rejected(self, client):
        request_payload = {
            "member_id": "EMP008",
            "treatment_date": "2024-09-21",
            "hospital": "Fortis",
            "is_network": True,
            "cashless_requested": False,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "Weight loss consultation",
                    "amount": 3000
                },
                {
                    "type": "pharmacy",
                    "description": "Diet plan",
                    "amount": 5000
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Gupta",
                "doctor_reg": "UP/33333/2016",
                "diagnosis": "Weight management",
                "services": ["Weight loss program", "Diet plan"],
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "REJECTED"
        assert "SERVICE_NOT_COVERED" in result["rejection_reasons"]
        assert "Weight loss treatments are excluded from coverage" in result["notes"]
        assert result["confidence_score"] == 0.97


class TestTC009NetworkHospital:
    """TC009: Network Hospital - Cashless Approved"""
    
    def test_tc009_network_hospital_cashless_approved(self, client):
        request_payload = {
            "member_id": "EMP009",
            "treatment_date": "2024-09-22",
            "hospital": "Apollo",
            "is_network": True,
            "cashless_requested": True,
            "line_items": [
                {
                    "type": "consultation",
                    "description": "General consultation",
                    "amount": 1500
                },
                {
                    "type": "pharmacy",
                    "description": "Generic medications",
                    "amount": 3000
                }
            ],
            "prescription": {
                "doctor_name": "Dr. Reddy",
                "doctor_reg": "TS/66666/2018",
                "diagnosis": "Common cold",
                "medicines": ["Paracetamol"],
                "valid": True
            }
        }
        
        response = client.post("/adjudicate", json=request_payload, headers={"X-API-Key": "local-dev"})
        assert response.status_code == 200
        
        result = response.get_json()
        assert result["decision"] == "APPROVED"
        assert result["approved_amount"] == 3600
        assert result["deductions"]["network_discount"] == 900
        assert result["cashless_approved"] == True
        assert result["confidence_score"] == 0.93


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "ok"
        assert "OPD Claim Adjudication" in result["service"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
