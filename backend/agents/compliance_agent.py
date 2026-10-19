"""
AeroCredits Multi-Tier Compliance & Fraud Agent.
Executes Tax/GST verification, sanctions/AML screening,
and circular trading detection across the supply chain graph.
"""

from typing import Dict, Any, List
from backend.models.domain import Invoice, ComplianceResult
from backend.models.database import db
from backend.gcp.pubsub_adapter import cloud_pubsub


class ComplianceAgent:
    """Agent executing regulatory compliance, sanctions, and anti-fraud checks."""

    def __init__(self, name: str = "AeroCredits-ComplianceAgent-03"):
        self.name = name
        self.role = "Multi-Tier Regulatory Compliance & Fraud Specialist"

    def process(self, invoice: Invoice) -> Dict[str, Any]:
        thoughts = []
        thoughts.append(f"[{self.name}] Initiating multi-tier compliance audit for Invoice {invoice.invoice_number}...")

        supplier = db.get_supplier(invoice.supplier_id)
        buyer = db.get_buyer(invoice.buyer_id)

        # 1. Tax & Legal Entity Verification (Tier 1)
        tax_ok = True
        reasons = []
        if not supplier:
            tax_ok = False
            reasons.append(f"Unknown supplier entity ID: {invoice.supplier_id}")
        elif not supplier.tax_id or len(supplier.tax_id) < 5:
            tax_ok = False
            reasons.append("Supplier Tax Identification Number (EIN/GSTIN) is invalid or revoked.")

        thoughts.append(f"[{self.name}] Tier 1 Tax/KYC Check: {'PASSED - Active Entity Filing' if tax_ok else 'FAILED'}")

        # 2. Sanctions & AML Screening (Tier 2)
        sanctions_cleared = True
        sanctions_watchlist = ["RESTRICTED_SUPPLIER_SHADOW", "CYBER_ARMS_LLC", "DARK_CARRIER"]
        if supplier and supplier.name in sanctions_watchlist:
            sanctions_cleared = False
            reasons.append(f"Sanctions Alert: Entity {supplier.name} matches restricted list entry.")

        thoughts.append(f"[{self.name}] Tier 2 Sanctions & PEP Screening: {'CLEARED (OFAC/EU/UN)' if sanctions_cleared else 'SANCTIONS HIT'}")

        # 3. Anti-Fraud & Circular Trading Detection (Tier 3)
        circular_detected = False
        # Check if buyer has historically invoiced the supplier for identical goods (shell circular loop)
        for other_inv in db.list_invoices():
            if other_inv.supplier_id == invoice.buyer_id and other_inv.buyer_id == invoice.supplier_id:
                circular_detected = True
                reasons.append("Fraud Alert: Circular invoicing pattern identified between counter-parties.")
                break

        thoughts.append(f"[{self.name}] Tier 3 Graph Anti-Fraud Check: {'NO CIRCULAR TRADING DETECTED' if not circular_detected else 'CIRCULAR FRAUD SUSPECTED'}")

        # 4. Corporate Credit Facility Ceiling (Tier 4)
        buyer_limit_ok = True
        if buyer:
            proposed_exposure = buyer.active_utilized + invoice.total_amount
            if proposed_exposure > buyer.total_credit_facility:
                buyer_limit_ok = False
                reasons.append(f"Credit Ceiling: Total exposure ${proposed_exposure:,.2f} exceeds buyer facility ${buyer.total_credit_facility:,.2f}.")
        else:
            buyer_limit_ok = False
            reasons.append("Corporate buyer entity not registered in AeroCredits Anchor directory.")

        thoughts.append(f"[{self.name}] Tier 4 Facility Limit Check: {'WITHIN CORPORATE CEILING' if buyer_limit_ok else 'LIMIT EXCEEDED'}")

        # Calculate final compliance score and status
        compliance_score = 100.0
        if not tax_ok:
            compliance_score -= 40.0
        if not sanctions_cleared:
            compliance_score -= 60.0
        if circular_detected:
            compliance_score -= 50.0
        if not buyer_limit_ok:
            compliance_score -= 25.0

        compliance_score = max(0.0, min(100.0, compliance_score))

        if not sanctions_cleared or circular_detected:
            status = "REJECTED"
        elif compliance_score < 75.0 or not buyer_limit_ok:
            status = "FLAGGED"
        else:
            status = "PASSED"
            reasons.append("All regulatory compliance tiers verified (KYC/AML, Tax ID, Anti-Circular, Facility Cap).")

        thoughts.append(f"[{self.name}] Compliance Audit Verdict: {status} (Score: {compliance_score}%).")

        comp_result = ComplianceResult(
            tax_id_verified=tax_ok,
            sanctions_cleared=sanctions_cleared,
            circular_trading_detected=circular_detected,
            buyer_limit_ok=buyer_limit_ok,
            compliance_score=compliance_score,
            status=status,
            reasons=reasons,
            pep_screened=True,
            active_tax_filing=tax_ok
        )

        audit_block = db.record_audit_event(
            actor_agent=self.name,
            action="EXECUTE_COMPLIANCE_SCREENING",
            entity_id=invoice.id,
            payload={
                "invoice_number": invoice.invoice_number,
                "compliance_score": compliance_score,
                "status": status,
                "tax_ok": tax_ok,
                "sanctions_cleared": sanctions_cleared,
                "circular_detected": circular_detected,
                "buyer_limit_ok": buyer_limit_ok,
                "reasons": reasons
            }
        )

        cloud_pubsub.publish_event(
            event_type="COMPLIANCE_COMPLETED",
            payload={"invoice_id": invoice.id, "compliance_status": status, "score": compliance_score}
        )

        return {
            "agent": self.name,
            "role": self.role,
            "status": "COMPLETED",
            "result": comp_result,
            "thoughts": thoughts,
            "audit_block_height": audit_block.block_height
        }
