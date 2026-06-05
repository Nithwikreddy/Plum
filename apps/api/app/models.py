from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class LineItem(BaseModel):
    type: str  # consultation, diagnostic, pharmacy, dental, alternative, vision, other
    description: str
    amount: float
    meta: Optional[Dict[str, Any]] = None


class Prescription(BaseModel):
    doctor_name: str
    doctor_reg: str
    diagnosis: str
    tests: Optional[List[str]] = None
    medicines: Optional[List[str]] = None
    procedures: Optional[List[str]] = None
    valid: bool = True


class Document(BaseModel):
    type: str  # prescription, bill, report, pharmacy_bill
    fields: Dict[str, Any]
    ocr_confidence: Optional[float] = None


class Member(BaseModel):
    id: str
    name: str
    join_date: datetime
    is_active: bool = True


class ClaimRequest(BaseModel):
    member_id: str
    treatment_date: str  # ISO format date
    hospital: str
    is_network: bool = False
    cashless_requested: bool = False
    line_items: List[LineItem]
    prescription: Optional[Prescription] = None
    documents: Optional[List[Document]] = None
    pre_auth_id: Optional[str] = None
    member_join_date: Optional[str] = None  # For test purposes
    previous_claims_same_day: Optional[int] = 0


class Deduction(BaseModel):
    copay: Optional[float] = None
    network_discount: Optional[float] = None


class Decision(BaseModel):
    claim_id: str
    decision: str  # APPROVED, REJECTED, PARTIAL, MANUAL_REVIEW
    approved_amount: Optional[float] = None
    rejection_reasons: Optional[List[str]] = None
    deductions: Optional[Deduction] = None
    rejected_items: Optional[List[str]] = None
    flags: Optional[List[str]] = None
    cashless_approved: Optional[bool] = None
    notes: str
    confidence_score: float
    next_steps: Optional[str] = None


class Claim(BaseModel):
    id: str
    member_id: str
    treatment_date: datetime
    hospital: str
    is_network: bool
    cashless_requested: bool
    line_items: List[LineItem]
    documents: Optional[List[Document]]
    status: str
    decision_json: Optional[Decision] = None
    created_at: datetime
