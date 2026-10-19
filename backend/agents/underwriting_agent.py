"""
AeroCredits Quantitative Risk & Underwriting Agent.
Dynamically computes Loan-to-Value (LTV) advance rates, annualized discount spreads,
tenure discounting fees, and net disbursement amounts.
"""

from typing import Dict, Any
from backend.models.domain import Invoice, ReconciliationResult, ComplianceResult, UnderwritingResult
from backend.models.database import db
from backend.config import BENCHMARK_INTEREST_RATE_APR, DEFAULT_ADVANCE_RATE_LTV
from backend.gcp.pubsub_adapter import cloud_pubsub


class UnderwritingAgent:
    """Agent executing quantitative credit underwriting, LTV sizing, and yield pricing."""

    def __init__(self, name: str = "AeroCredits-UnderwriteAgent-04"):
        self.name = name
        self.role = "Quantitative Credit Underwriter & Pricing Specialist"

    def process(self, invoice: Invoice, reconcile: ReconciliationResult, compliance: ComplianceResult) -> Dict[str, Any]:
        thoughts = []
        thoughts.append(f"[{self.name}] Initiating algorithmic underwriting for Invoice {invoice.invoice_number}...")

        buyer = db.get_buyer(invoice.buyer_id)
        supplier = db.get_supplier(invoice.supplier_id)

        buyer_tier = buyer.enterprise_tier if buyer else "BBB"
        buyer_score = buyer.credit_score if buyer else 700

        # Spread matrix based on anchor buyer enterprise tier
        tier_spread_map = {
            "AAA": 1.75,
            "AA+": 2.25,
            "AA": 2.75,
            "A+": 3.25,
            "A": 3.75,
            "BBB+": 4.50,
            "BBB": 5.25
        }
        risk_spread = tier_spread_map.get(buyer_tier, 5.50)

        # Reconciliation score adjustment
        if reconcile.line_item_score < 95.0:
            risk_spread += 1.50
        if compliance.status == "FLAGGED":
            risk_spread += 2.00

        annualized_apr = round(BENCHMARK_INTEREST_RATE_APR + risk_spread, 2)
        thoughts.append(f"[{self.name}] Risk Pricing: Benchmark {BENCHMARK_INTEREST_RATE_APR}% + Risk Spread {risk_spread}% = {annualized_apr}% APR.")

        # Determine Advance Rate (LTV)
        advance_ltv = DEFAULT_ADVANCE_RATE_LTV
        if buyer_tier in ("AAA", "AA+"):
            advance_ltv = 90.0
        elif buyer_tier in ("AA", "A+"):
            advance_ltv = 85.0
        else:
            advance_ltv = 80.0

        if reconcile.line_item_score < 95.0:
            advance_ltv -= 5.0

        # Tenure days (from buyer terms or default 60)
        tenure_days = buyer.payment_terms_days if buyer else 60

        # Calculations
        loan_principal = round(invoice.total_amount * (advance_ltv / 100.0), 2)
        daily_rate = (annualized_apr / 100.0) / 365.0
        discount_fee = round(loan_principal * daily_rate * tenure_days, 2)
        net_disbursement = round(loan_principal - discount_fee, 2)

        # Risk tiering
        if buyer_score >= 850 and reconcile.line_item_score >= 95.0 and compliance.status == "PASSED":
            risk_tier = "LOW_RISK"
        elif buyer_score >= 740 and reconcile.line_item_score >= 88.0 and compliance.status != "REJECTED":
            risk_tier = "MEDIUM_RISK"
        else:
            risk_tier = "ELEVATED_RISK"

        pricing_rationale = (
            f"Anchor Buyer {buyer.name if buyer else 'Enterprise'} rated {buyer_tier} ({buyer_score} score). "
            f"Advance rate set to {advance_ltv}% of verified invoice total (${invoice.total_amount:,.2f}). "
            f"Priced at {annualized_apr}% APR for {tenure_days} days tenure. "
            f"Discount fee ${discount_fee:,.2f} yielding net cash disbursement of ${net_disbursement:,.2f}."
        )

        thoughts.append(f"[{self.name}] Principal Advance: ${loan_principal:,.2f} ({advance_ltv}% LTV) | Net Cash: ${net_disbursement:,.2f} | Risk: {risk_tier}.")

        uw_result = UnderwritingResult(
            buyer_credit_score=buyer_score,
            recommended_ltv_percent=advance_ltv,
            loan_principal_advance=loan_principal,
            annualized_discount_rate=annualized_apr,
            tenure_days=tenure_days,
            discount_fee=discount_fee,
            net_disbursement=net_disbursement,
            risk_tier=risk_tier,
            pricing_rationale=pricing_rationale
        )

        audit_block = db.record_audit_event(
            actor_agent=self.name,
            action="EXECUTE_CREDIT_UNDERWRITING",
            entity_id=invoice.id,
            payload={
                "invoice_number": invoice.invoice_number,
                "advance_ltv_percent": advance_ltv,
                "loan_principal_advance": loan_principal,
                "annualized_apr": annualized_apr,
                "tenure_days": tenure_days,
                "discount_fee": discount_fee,
                "net_disbursement": net_disbursement,
                "risk_tier": risk_tier
            }
        )

        cloud_pubsub.publish_event(
            event_type="UNDERWRITING_COMPLETED",
            payload={"invoice_id": invoice.id, "principal": loan_principal, "net_disbursement": net_disbursement}
        )

        return {
            "agent": self.name,
            "role": self.role,
            "status": "COMPLETED",
            "result": uw_result,
            "thoughts": thoughts,
            "audit_block_height": audit_block.block_height
        }
