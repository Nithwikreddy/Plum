from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    join_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    claims = db.relationship('Claim', backref='member', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'join_date': self.join_date.isoformat(),
            'is_active': self.is_active
        }


class LineItem(db.Model):
    __tablename__ = 'line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), db.ForeignKey('claims.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # consultation, diagnostic, pharmacy, dental, alternative
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    meta = db.Column(db.JSON, nullable=True)
    
    def to_dict(self):
        return {
            'type': self.type,
            'description': self.description,
            'amount': self.amount,
            'meta': self.meta
        }


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), db.ForeignKey('claims.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # prescription, bill, report, pharmacy_bill
    fields = db.Column(db.JSON, nullable=False)
    ocr_confidence = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'type': self.type,
            'fields': self.fields,
            'ocr_confidence': self.ocr_confidence
        }


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), db.ForeignKey('claims.id'), nullable=True, unique=True)
    doctor_name = db.Column(db.String(255), nullable=False)
    doctor_reg = db.Column(db.String(50), nullable=False)
    diagnosis = db.Column(db.String(500), nullable=False)
    tests = db.Column(db.JSON, nullable=True)  # List of tests
    medicines = db.Column(db.JSON, nullable=True)  # List of medicines
    procedures = db.Column(db.JSON, nullable=True)  # List of procedures
    valid = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'doctor_name': self.doctor_name,
            'doctor_reg': self.doctor_reg,
            'diagnosis': self.diagnosis,
            'tests': self.tests,
            'medicines': self.medicines,
            'procedures': self.procedures,
            'valid': self.valid
        }


class Claim(db.Model):
    __tablename__ = 'claims'
    
    id = db.Column(db.String(50), primary_key=True)
    member_id = db.Column(db.String(50), db.ForeignKey('members.id'), nullable=False)
    treatment_date = db.Column(db.DateTime, nullable=False)
    hospital = db.Column(db.String(255), nullable=False)
    is_network = db.Column(db.Boolean, default=False)
    cashless_requested = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='SUBMITTED')  # SUBMITTED, APPROVED, REJECTED, PARTIAL, MANUAL_REVIEW
    decision_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    line_items = db.relationship('LineItem', backref='claim', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='claim', lazy=True, cascade='all, delete-orphan')
    prescription = db.relationship('Prescription', backref='claim', lazy=True, cascade='all, delete-orphan', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'treatment_date': self.treatment_date.isoformat(),
            'hospital': self.hospital,
            'is_network': self.is_network,
            'cashless_requested': self.cashless_requested,
            'status': self.status,
            'line_items': [item.to_dict() for item in self.line_items],
            'documents': [doc.to_dict() for doc in self.documents],
            'prescription': self.prescription.to_dict() if self.prescription else None,
            'decision_json': self.decision_json,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
