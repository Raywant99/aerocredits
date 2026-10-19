"""
AeroCredits Domain Models
Defines enterprise data structures for B2B Supply Chain Invoice Loan Engine.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime


class ParticipantRole:
    SUPPLIER = "SUPPLIER"
    BUYER = "BUYER"
    LENDER = "LENDER"
    AUDITOR = "AUDITOR"


class Supplier(BaseModel):
    id: str
    name: str
    tax_id: str
    country: str
    industry: str
    credit_rating: str
    kyc_status: str = "VERIFIED"
    bank_account: str
    credit_limit: float
    utilized_limit: float = 0.0


class Buyer(BaseModel):
    id: str
    name: str
    tax_id: str
    country: str
    enterprise_tier: str  # AAA, AA+, AA, A
    credit_score: int
    payment_terms_days: int = 60
    total_credit_facility: float
    active_utilized: float = 0.0


class Lender(BaseModel):
    id: str
    name: str
    available_capital: float
    deployed_capital: float
    min_discount_rate_apr: float
    risk_tolerance: str  # CONSERVATIVE, BALANCED, GROWTH
    authorized_officer: str


class InvoiceLineItem(BaseModel):
    item_id: str
    sku: str
    description: str
    ordered_quantity: float
    billed_quantity: float
    unit_price: float
    line_total: float
    hs_code: Optional[str] = "8411.91.00"


class PurchaseOrder(BaseModel):
    po_number: str
    buyer_id: str
    supplier_id: str
    issue_date: str
    total_authorized: float
    currency: str = "USD"
    line_items: List[InvoiceLineItem]
    status: str = "CONFIRMED"


class LogisticsWaybill(BaseModel):
    waybill_number: str
    carrier: str  # FedEx Freight, Maersk Logistics, DHL Global Forwarding
    tracking_number: str
    origin_hub: str
    destination_facility: str
    delivery_timestamp: str
    delivered_quantities: Dict[str, float]  # SKU -> quantity delivered
    recipient_signoff: str
    pod_hash: str
    status: str = "DELIVERED_VERIFIED"


class Invoice(BaseModel):
    id: str
    invoice_number: str
    supplier_id: str
    buyer_id: str
    issue_date: str
    due_date: str
    currency: str = "USD"
    subtotal: float
    tax_amount: float
    total_amount: float
    po_number: str
    waybill_number: str
    line_items: List[InvoiceLineItem]
    gcs_uri: str = "gs://aerocredits-vault/invoices/unassigned.pdf"
    file_sha256: str = ""
    status: str = "INGESTED"


class ItemVariance(BaseModel):
    sku: str
    description: str
    ordered_qty: float
    billed_qty: float
    delivered_qty: float
    unit_price_po: float
    unit_price_inv: float
    qty_match: bool
    price_match: bool
    status: str


class ReconciliationResult(BaseModel):
    po_match: bool
    logistics_match: bool
    line_item_score: float  # 0 to 100
    quantity_variance_percent: float
    price_variance_percent: float
    item_variances: List[ItemVariance] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)
    confidence_score: float = 98.5


class ComplianceResult(BaseModel):
    tax_id_verified: bool
    sanctions_cleared: bool
    circular_trading_detected: bool
    buyer_limit_ok: bool
    compliance_score: float
    status: str  # PASSED, FLAGGED, REJECTED
    reasons: List[str] = Field(default_factory=list)
    pep_screened: bool = True
    active_tax_filing: bool = True


class UnderwritingResult(BaseModel):
    buyer_credit_score: int
    recommended_ltv_percent: float  # e.g., 85.0%
    loan_principal_advance: float
    annualized_discount_rate: float  # e.g., 7.8% APR
    tenure_days: int
    discount_fee: float
    net_disbursement: float
    risk_tier: str  # LOW_RISK, MEDIUM_RISK, ELEVATED_RISK
    pricing_rationale: str


class LoanRequest(BaseModel):
    id: str
    invoice_id: str
    supplier_id: str
    buyer_id: str
    lender_id: Optional[str] = None
    requested_amount: float
    tenure_days: int = 60
    reconciliation: Optional[ReconciliationResult] = None
    compliance: Optional[ComplianceResult] = None
    underwriting: Optional[UnderwritingResult] = None
    approval_status: str = "PENDING_AUDIT"
    approval_tier: str = "TIER_1_AUTO"  # TIER_1_AUTO, TIER_2_HITL
    hitl_reason: Optional[str] = None
    hitl_decision: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class AuditBlock(BaseModel):
    block_height: int
    timestamp: str
    actor_agent: str
    action: str
    entity_id: str
    data_payload: Dict[str, Any]
    previous_hash: str
    block_hash: str

    @classmethod
    def create(cls, block_height: int, actor_agent: str, action: str, entity_id: str, data_payload: Dict[str, Any], previous_hash: str) -> "AuditBlock":
        ts = datetime.utcnow().isoformat() + "Z"
        payload_str = json.dumps(data_payload, sort_keys=True)
        raw_to_hash = f"{block_height}|{ts}|{actor_agent}|{action}|{entity_id}|{payload_str}|{previous_hash}"
        block_hash = hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()
        return cls(
            block_height=block_height,
            timestamp=ts,
            actor_agent=actor_agent,
            action=action,
            entity_id=entity_id,
            data_payload=data_payload,
            previous_hash=previous_hash,
            block_hash=block_hash,
        )
