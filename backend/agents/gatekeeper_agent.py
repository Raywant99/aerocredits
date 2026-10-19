"""
AeroCredits Governance & Approval Gatekeeper Agent.
Enforces multi-tier compliance policies and manages the Human-In-The-Loop (HITL)
approval gate for high-value loans and variance anomalies.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from backend.models.domain import Invoice, ReconciliationResult, ComplianceResult, UnderwritingResult, LoanRequest
from backend.models.database import db
from backend.config import HITL_LOAN_THRESHOLD_USD, MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL
from backend.gcp.pubsub_adapter import cloud_pubsub


class GatekeeperAgent:
    """Agent evaluating auto-approval criteria vs HITL escalation gates."""

    def __init__(self, name: str = "AeroCredits-Gatekeeper-05"):
        self.name = name
        self.role = "Governance & Approval Gatekeeper Specialist"

    def process(
        self,
        invoice: Invoice,
        reconcile: ReconciliationResult,
        compliance: ComplianceResult,
        underwriting: UnderwritingResult
    ) -> Dict[str, Any]:
        thoughts = []
        thoughts.append(f"[{self.name}] Evaluating governance rules for Loan Request on Invoice {invoice.invoice_number}...")

        loan_id = f"loan_{invoice.id.replace('inv_', '')}"
        loan_amount = invoice.total_amount

        # Check rejection criteria
        if compliance.status == "REJECTED":
            status = "REJECTED"
            tier = "TIER_3_REJECT"
            reason = f"Loan auto-rejected due to critical compliance failure: {'; '.join(compliance.reasons)}"
            thoughts.append(f"[{self.name}] CRITICAL: Rejection triggered -> {reason}")
            lender_id = None

        # Check Human-in-the-loop (HITL) escalation gates
        elif loan_amount >= HITL_LOAN_THRESHOLD_USD:
            status = "ESCALATED_HITL"
            tier = "TIER_2_HITL"
            reason = (
                f"High-Value Policy Gate: Invoice amount (${loan_amount:,.2f}) meets or exceeds the "
                f"${HITL_LOAN_THRESHOLD_USD:,.2f} enterprise threshold. Mandatory Human-In-The-Loop lender sign-off required."
            )
            thoughts.append(f"[{self.name}] ESCALATION: High-value loan policy triggered. Pausing automated disbursement for human officer review.")
            lender_id = "lender_001"

        elif reconcile.line_item_score < MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL:
            status = "ESCALATED_HITL"
            tier = "TIER_2_HITL"
            reason = (
                f"Variance Gate: 3-way reconciliation score ({reconcile.line_item_score}%) is below the "
                f"auto-approval threshold ({MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL}%). Discrepancy requires credit officer verification."
            )
            thoughts.append(f"[{self.name}] ESCALATION: Logistics line-item variance requires human intervention.")
            lender_id = "lender_001"

        elif compliance.status == "FLAGGED":
            status = "ESCALATED_HITL"
            tier = "TIER_2_HITL"
            reason = f"Compliance Review Gate: Non-fatal compliance flags detected: {'; '.join(compliance.reasons)}"
            thoughts.append(f"[{self.name}] ESCALATION: Compliance flagged item requires manual officer waiver.")
            lender_id = "lender_001"

        else:
            # Auto-approval criteria met!
            status = "AUTO_APPROVED"
            tier = "TIER_1_AUTO"
            reason = (
                f"Auto-Approval Cleared: Loan amount (${loan_amount:,.2f} < ${HITL_LOAN_THRESHOLD_USD:,.2f}), "
                f"3-way match {reconcile.line_item_score}% >= {MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL}%, "
                f"and full compliance certification confirmed. Routing directly to Lender Liquidity Pool for disbursement."
            )
            thoughts.append(f"[{self.name}] SUCCESS: Tier-1 Auto-Approval granted. Zero manual friction.")

            # Assign to best matching lender
            lenders = db.list_lenders()
            selected_lender = lenders[0] if lenders else None
            lender_id = selected_lender.id if selected_lender else "lender_001"

            # Auto-disburse
            if selected_lender and selected_lender.available_capital >= underwriting.net_disbursement:
                db.update_lender_deployment(selected_lender.id, underwriting.net_disbursement)
                status = "DISBURSED"
                thoughts.append(f"[{self.name}] DISBURSED: ${underwriting.net_disbursement:,.2f} transferred to Supplier bank account via {selected_lender.name}.")

        loan_obj = LoanRequest(
            id=loan_id,
            invoice_id=invoice.id,
            supplier_id=invoice.supplier_id,
            buyer_id=invoice.buyer_id,
            lender_id=lender_id,
            requested_amount=loan_amount,
            tenure_days=underwriting.tenure_days,
            reconciliation=reconcile,
            compliance=compliance,
            underwriting=underwriting,
            approval_status=status,
            approval_tier=tier,
            hitl_reason=reason,
            created_at=datetime.utcnow().isoformat() + "Z",
            updated_at=datetime.utcnow().isoformat() + "Z"
        )

        db.add_loan(loan_obj)

        audit_block = db.record_audit_event(
            actor_agent=self.name,
            action="GOVERNANCE_DECISION_AND_ROUTING",
            entity_id=loan_obj.id,
            payload={
                "loan_id": loan_obj.id,
                "invoice_number": invoice.invoice_number,
                "loan_amount": loan_amount,
                "approval_status": status,
                "approval_tier": tier,
                "reason": reason,
                "disbursed_amount": underwriting.net_disbursement if status == "DISBURSED" else 0.0,
                "lender_id": lender_id
            }
        )

        cloud_pubsub.publish_event(
            event_type="LOAN_DECISION_EMITTED",
            payload={"loan_id": loan_obj.id, "status": status, "tier": tier}
        )

        return {
            "agent": self.name,
            "role": self.role,
            "status": "COMPLETED",
            "loan": loan_obj,
            "thoughts": thoughts,
            "audit_block_height": audit_block.block_height
        }
