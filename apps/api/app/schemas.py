from typing import Optional, List, Dict, Any


class LineItemSchema:
    def __init__(self, type: str, description: str, amount: float, meta: Optional[Dict[str, Any]] = None):
        self.type = type
        self.description = description
        self.amount = amount
        self.meta = meta

    def dict(self):
        return {
            'type': self.type,
            'description': self.description,
            'amount': self.amount,
            'meta': self.meta
        }


class PrescriptionSchema:
    def __init__(self, doctor_name: str, doctor_reg: str, diagnosis: str, tests: Optional[List[str]] = None, medicines: Optional[List[str]] = None, procedures: Optional[List[str]] = None, valid: bool = True):
        self.doctor_name = doctor_name
        self.doctor_reg = doctor_reg
        self.diagnosis = diagnosis
        self.tests = tests
        self.medicines = medicines
        self.procedures = procedures
        self.valid = valid

    def dict(self):
        return {
            'doctor_name': self.doctor_name,
            'doctor_reg': self.doctor_reg,
            'diagnosis': self.diagnosis,
            'tests': self.tests,
            'medicines': self.medicines,
            'procedures': self.procedures,
            'valid': self.valid
        }


class DocumentSchema:
    def __init__(self, type: str, fields: Dict[str, Any], ocr_confidence: Optional[float] = None):
        self.type = type
        self.fields = fields
        self.ocr_confidence = ocr_confidence

    def dict(self):
        return {'type': self.type, 'fields': self.fields, 'ocr_confidence': self.ocr_confidence}


class ClaimRequestSchema:
    def __init__(self, **data):
        # Simple shim: accept dict and provide .dict()
        self._data = data

    def dict(self):
        return self._data


class DecisionSchema:
    pass

