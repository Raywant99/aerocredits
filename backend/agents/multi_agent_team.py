"""
AeroCredits Autonomous Multi-Agent Financial Audit & Reconciliation Team.
Utilizes the Antigravity SDK architecture and Google Cloud integration
to orchestrate Ingestion, 3-Way Reconciliation, Compliance, Underwriting, and Governance.
"""

import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.agents.ingestion_agent import IngestionAgent
from backend.agents.reconciliation_agent import ReconciliationAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.underwriting_agent import UnderwritingAgent
from backend.agents.gatekeeper_agent import GatekeeperAgent
from backend.models.database import db
from backend.config import ANTIGRAVITY_MODEL, USE_LIVE_VERTEX


class MultiAgentAuditTeam:
    """Orchestrates the Antigravity autonomous multi-agent financial audit pipeline."""

    def __init__(self):
        self.ingestion_agent = IngestionAgent()
        self.reconciliation_agent = ReconciliationAgent()
        self.compliance_agent = ComplianceAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.gatekeeper_agent = GatekeeperAgent()

    def run_pipeline(self, invoice_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes end-to-end multi-agent audit on an invoice:
        1. Ingestion & GCS line-item extraction
        2. 3-Way Reconciliation (PO vs Inv vs Logistics Waybill)
        3. Multi-tier compliance check (Tax ID, AML/Sanctions, Anti-Circular)
        4. Quantitative credit underwriting (LTV, APR, Discount fee)
        5. Gatekeeper governance (Auto-approval vs HITL escalation)
        """
        start_time = time.time()
        pipeline_log = []

        # --- Phase 1: Document Ingestion & Extraction ---
        t0 = time.time()
        ingestion_res = self.ingestion_agent.process(invoice_input)
        invoice = ingestion_res["invoice"]
        pipeline_log.append({
            "stage": "INGESTION_EXTRACTION",
            "agent": ingestion_res["agent"],
            "role": ingestion_res["role"],
            "duration_ms": round((time.time() - t0) * 1000, 2),
            "thoughts": ingestion_res["thoughts"],
            "status": ingestion_res["status"],
            "summary": f"Ingested {len(invoice.line_items)} line items. Total face value: ${invoice.total_amount:,.2f}"
        })

        # --- Phase 2: 3-Way Line Item Reconciliation ---
        t1 = time.time()
        reconcile_res = self.reconciliation_agent.process(invoice)
        reconcile = reconcile_res["result"]
        pipeline_log.append({
            "stage": "3_WAY_RECONCILIATION",
            "agent": reconcile_res["agent"],
            "role": reconcile_res["role"],
            "duration_ms": round((time.time() - t1) * 1000, 2),
            "thoughts": reconcile_res["thoughts"],
            "status": reconcile_res["status"],
            "score": reconcile.line_item_score,
            "summary": f"3-Way Reconciliation score: {reconcile.line_item_score}% (Qty Var: {reconcile.quantity_variance_percent}%, Price Var: {reconcile.price_variance_percent}%)"
        })

        # --- Phase 3: Multi-Tier Compliance & Sanctions ---
        t2 = time.time()
        compliance_res = self.compliance_agent.process(invoice)
        compliance = compliance_res["result"]
        pipeline_log.append({
            "stage": "COMPLIANCE_SCREENING",
            "agent": compliance_res["agent"],
            "role": compliance_res["role"],
            "duration_ms": round((time.time() - t2) * 1000, 2),
            "thoughts": compliance_res["thoughts"],
            "status": compliance_res["status"],
            "compliance_status": compliance.status,
            "score": compliance.compliance_score,
            "summary": f"Compliance status: {compliance.status} (Score: {compliance.compliance_score}%)"
        })

        # --- Phase 4: Quantitative Risk & Underwriting ---
        t3 = time.time()
        underwrite_res = self.underwriting_agent.process(invoice, reconcile, compliance)
        underwriting = underwrite_res["result"]
        pipeline_log.append({
            "stage": "CREDIT_UNDERWRITING",
            "agent": underwrite_res["agent"],
            "role": underwrite_res["role"],
            "duration_ms": round((time.time() - t3) * 1000, 2),
            "thoughts": underwrite_res["thoughts"],
            "status": underwrite_res["status"],
            "advance_principal": underwriting.loan_principal_advance,
            "net_cash": underwriting.net_disbursement,
            "apr": underwriting.annualized_discount_rate,
            "summary": f"Underwritten at {underwriting.annualized_discount_rate}% APR. Advance: ${underwriting.loan_principal_advance:,.2f} ({underwriting.recommended_ltv_percent}% LTV)"
        })

        # --- Phase 5: Governance & Gatekeeper Decision ---
        t4 = time.time()
        gatekeeper_res = self.gatekeeper_agent.process(invoice, reconcile, compliance, underwriting)
        loan = gatekeeper_res["loan"]
        pipeline_log.append({
            "stage": "GOVERNANCE_GATEKEEPER",
            "agent": gatekeeper_res["agent"],
            "role": gatekeeper_res["role"],
            "duration_ms": round((time.time() - t4) * 1000, 2),
            "thoughts": gatekeeper_res["thoughts"],
            "status": gatekeeper_res["status"],
            "approval_status": loan.approval_status,
            "approval_tier": loan.approval_tier,
            "summary": f"Decision: {loan.approval_status} ({loan.approval_tier}). {loan.hitl_reason}"
        })

        total_elapsed = round(time.time() - start_time, 2)

        return {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "loan_id": loan.id,
            "total_face_value": invoice.total_amount,
            "net_disbursement": underwriting.net_disbursement,
            "approval_status": loan.approval_status,
            "approval_tier": loan.approval_tier,
            "hitl_reason": loan.hitl_reason,
            "total_execution_seconds": total_elapsed,
            "pipeline_log": pipeline_log,
            "invoice": invoice.dict(),
            "loan": loan.dict(),
            "latest_audit_block": db.get_audit_trail(1)[0].dict() if db.audit_chain else None
        }


# Global multi-agent team instance
multi_agent_team = MultiAgentAuditTeam()
