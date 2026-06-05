from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import json
from pathlib import Path
import uuid

from app.db_models import db, Member, Claim, LineItem, Document, Prescription
from app.schemas import ClaimRequestSchema
from app.rules.engine import RuleEngine, PolicyConfig
from app.config import config


def create_app(config_name='development'):
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Global rule engine and policy config
    app.rule_engine = None
    app.policy_config = None
    
    @app.before_request
    def initialize_engine():
        """Initialize rule engine on first request"""
        if app.rule_engine is None:
            # Load policy configuration
            policy_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared" / "policy_terms.json"
            if not policy_path.exists():
                raise FileNotFoundError(f"Policy file not found at {policy_path}")
            
            app.policy_config = PolicyConfig.from_json(str(policy_path))
            app.rule_engine = RuleEngine(app.policy_config)
            
            # Register test members
            test_members = {
                "EMP001": ("Ramesh Kumar", "2024-09-01"),
                "EMP002": ("Priya Singh", "2024-09-01"),
                "EMP003": ("Amit Patel", "2024-09-01"),
                "EMP004": ("Neha Verma", "2024-09-01"),
                "EMP005": ("Rajesh Kumar", "2024-09-01"),
                "EMP006": ("Deepak Sharma", "2024-09-01"),
                "EMP007": ("Sanjay Gupta", "2024-09-01"),
                "EMP008": ("Vikram Reddy", "2024-09-01"),
                "EMP009": ("Arjun Singh", "2024-09-01"),
            }
            
            for member_id, (name, join_date) in test_members.items():
                app.rule_engine.register_member(
                    member_id,
                    name,
                    datetime.strptime(join_date, "%Y-%m-%d")
                )
                
                # Save to database
                member = Member.query.get(member_id)
                if not member:
                    member = Member(
                        id=member_id,
                        name=name,
                        join_date=datetime.strptime(join_date, "%Y-%m-%d")
                    )
                    db.session.add(member)
            
            db.session.commit()
    
    def require_api_key(f):
        """Decorator to check API key"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get(app.config['API_KEY_HEADER'])
            if api_key and api_key != app.config['API_KEY_VALUE']:
                return jsonify({'detail': 'Invalid API key'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'service': 'OPD Claim Adjudication API',
            'version': '1.0.0'
        })
    
    @app.route('/claims', methods=['POST'])
    @require_api_key
    def create_claim():
        """Create and adjudicate a claim"""
        try:
            data = request.get_json()
            
            # Validate request using Pydantic schema
            claim_request = ClaimRequestSchema(**data)
            claim_dict = claim_request.dict()
            
            # Generate claim ID
            claim_id = f"CLM_{uuid.uuid4().hex[:8].upper()}"
            
            # Run adjudication
            decision = app.rule_engine.adjudicate_claim(claim_dict)
            decision['claim_id'] = claim_id
            
            # Save to database
            member_id = claim_dict['member_id']
            treatment_date = datetime.strptime(claim_dict['treatment_date'], '%Y-%m-%d')
            
            claim = Claim(
                id=claim_id,
                member_id=member_id,
                treatment_date=treatment_date,
                hospital=claim_dict['hospital'],
                is_network=claim_dict.get('is_network', False),
                cashless_requested=claim_dict.get('cashless_requested', False),
                status=decision['decision'],
                decision_json=decision
            )
            
            # Add line items
            for item in claim_dict['line_items']:
                line_item = LineItem(
                    claim=claim,
                    type=item['type'],
                    description=item['description'],
                    amount=item['amount'],
                    meta=item.get('meta')
                )
                db.session.add(line_item)
            
            # Add documents
            if claim_dict.get('documents'):
                for doc in claim_dict['documents']:
                    document = Document(
                        claim=claim,
                        type=doc['type'],
                        fields=doc['fields'],
                        ocr_confidence=doc.get('ocr_confidence')
                    )
                    db.session.add(document)
            
            # Add prescription
            if claim_dict.get('prescription'):
                prescription = Prescription(
                    claim=claim,
                    doctor_name=claim_dict['prescription']['doctor_name'],
                    doctor_reg=claim_dict['prescription']['doctor_reg'],
                    diagnosis=claim_dict['prescription']['diagnosis'],
                    tests=claim_dict['prescription'].get('tests'),
                    medicines=claim_dict['prescription'].get('medicines'),
                    procedures=claim_dict['prescription'].get('procedures'),
                    valid=claim_dict['prescription'].get('valid', True)
                )
                db.session.add(prescription)
            
            db.session.add(claim)
            db.session.commit()
            
            return jsonify(decision), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'detail': str(e)}), 400
    
    @app.route('/claims/<claim_id>', methods=['GET'])
    @require_api_key
    def get_claim(claim_id):
        """Get claim details"""
        try:
            claim = Claim.query.get(claim_id)
            if not claim:
                return jsonify({'detail': 'Claim not found'}), 404
            
            return jsonify(claim.to_dict())
        except Exception as e:
            return jsonify({'detail': str(e)}), 400
    
    @app.route('/adjudicate', methods=['POST'])
    @require_api_key
    def adjudicate():
        """Adjudicate a claim directly"""
        try:
            data = request.get_json()
            
            # Validate request
            claim_request = ClaimRequestSchema(**data)
            claim_dict = claim_request.dict()
            
            # Run adjudication
            decision = app.rule_engine.adjudicate_claim(claim_dict)
            
            return jsonify(decision)
        except Exception as e:
            return jsonify({'detail': str(e)}), 400

    @app.route('/run-tests', methods=['GET'])
    @require_api_key
    def run_tests():
        """Run seeded test cases through the rule engine and return results"""
        try:
            policy_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared" / "test_cases.json"
            with open(policy_path, 'r') as f:
                tests = json.load(f).get('test_cases', [])

            results = []
            for tc in tests:
                inputs = tc['inputs']
                expected = tc.get('expected_output', {})

                decision = app.rule_engine.adjudicate_claim(inputs)

                passed = True
                details = {'expected': expected, 'actual': decision}

                # Check decision
                if expected.get('decision') and decision.get('decision') != expected.get('decision'):
                    passed = False

                # Check approved_amount if present
                if 'approved_amount' in expected:
                    if float(decision.get('approved_amount') or 0) != float(expected.get('approved_amount')):
                        passed = False

                # Check deductions keys
                if expected.get('deductions'):
                    for k, v in expected['deductions'].items():
                        if not decision.get('deductions') or float(decision['deductions'].get(k, 0) or 0) != float(v):
                            passed = False

                # Check flags/rejection_reasons presence
                if expected.get('flags'):
                    for flag in expected['flags']:
                        if flag not in (decision.get('flags') or []):
                            passed = False
                if expected.get('rejection_reasons'):
                    for reason in expected['rejection_reasons']:
                        if reason not in (decision.get('rejection_reasons') or []):
                            passed = False

                # Check notes contains expected notes text when provided
                if expected.get('notes'):
                    def _normalize_notes(s: str) -> str:
                        if not s:
                            return ''
                        # fix common mojibake for rupee sign and normalize whitespace
                        s = s.replace('â‚¹', '₹')
                        s = s.replace('\u20b9', '₹')
                        s = s.replace('Â', '')
                        return ' '.join(s.split())

                    expected_notes = _normalize_notes(expected['notes'])
                    actual_notes = _normalize_notes(decision.get('notes') or '')
                    if expected_notes not in actual_notes:
                        passed = False

                # Check confidence roughly equals
                if 'confidence_score' in expected:
                    if round(float(decision.get('confidence_score') or 0), 2) != round(float(expected.get('confidence_score')), 2):
                        passed = False

                results.append({
                    'test_id': tc.get('tc_id'),
                    'name': tc.get('name'),
                    'passed': passed,
                    'expected': expected,
                    'actual': decision
                })

            return jsonify({'results': results})
        except Exception as e:
            return jsonify({'detail': str(e)}), 500
    
    @app.route('/members', methods=['GET'])
    @require_api_key
    def list_members():
        """List all members"""
        try:
            members = Member.query.all()
            return jsonify([member.to_dict() for member in members])
        except Exception as e:
            return jsonify({'detail': str(e)}), 400
    
    @app.route('/members/<member_id>', methods=['GET'])
    @require_api_key
    def get_member(member_id):
        """Get member details"""
        try:
            member = Member.query.get(member_id)
            if not member:
                return jsonify({'detail': 'Member not found'}), 404
            
            return jsonify(member.to_dict())
        except Exception as e:
            return jsonify({'detail': str(e)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'detail': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'detail': 'Internal server error'}), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
    
