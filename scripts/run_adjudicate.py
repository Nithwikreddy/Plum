from pathlib import Path
from app.rules.engine import PolicyConfig, RuleEngine
from datetime import datetime
import json
policy_path = Path('packages/shared/policy_terms.json')
pc = PolicyConfig.from_json(str(policy_path))
eng = RuleEngine(npc)
eng.register_member('EMP002','Priya Singh', datetime.strptime('2024-09-01','%Y-%m-%d'))
claim = {
    "member_id": "EMP002",
    "treatment_date": "2024-09-16",
    "hospital": "Max",
    "is_network": True,
    "cashless_requested": False,
    "line_items": [
        {"type":"dental","description":"Root canal","amount":8000},
        {"type":"dental","description":"Teeth whitening","amount":4000}
    ],
    "prescription": {
        "doctor_name": "Dr. Patel",
        "doctor_reg": "GJ/12345/2018",
        "diagnosis": "Dental caries",
        "procedures": ["Root canal","Teeth whitening"],
        "valid": True
    }
}
res = eng.adjudicate_claim(claim)
print(json.dumps(res, indent=2))
