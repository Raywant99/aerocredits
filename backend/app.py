"""
AeroCredits REST API & Server Application.
Enterprise backend for B2B Supply Chain Invoice Loan Engine,
powered by Google Cloud integration and Antigravity Multi-Agent Audit Team.
"""

import os
import sys
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response

# Add parent directory to path so relative imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import (
    PORT, HOST, DEBUG, HITL_LOAN_THRESHOLD_USD,
    MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL,
    GCP_PROJECT_ID, GCS_BUCKET_INVOICES, ANTIGRAVITY_MODEL, USE_LIVE_VERTEX
)
from backend.models.database import db
from backend.seed_data import load_seed_data
from backend.agents.multi_agent_team import multi_agent_team
from backend.gcp.storage_adapter import cloud_storage
from backend.gcp.pubsub_adapter import cloud_pubsub

# Frontend static paths
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

# Initialize seed data on startup
load_seed_data()


# --- Static UI Serving ---
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)


# --- System Health & Configuration ---
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "HEALTHY",
        "service": "AeroCredits B2B Supply Chain Invoice Loan Engine",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "antigravity_sdk": {
            "model": ANTIGRAVITY_MODEL,
            "engine": "Antigravity Autonomous Multi-Agent Audit Team",
            "live_vertex_enabled": USE_LIVE_VERTEX
        },
        "google_cloud": {
            "project_id": GCP_PROJECT_ID,
            "inbound_bucket": GCS_BUCKET_INVOICES,
            "pubsub_topic": "projects/aerocredits-enterprise-cloud/topics/invoice-events"
        },
        "hitl_policy": {
            "threshold_usd": HITL_LOAN_THRESHOLD_USD,
            "min_reconcile_score": MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL
        }
    })


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    metrics = db.get_metrics()
    return jsonify({"success": True, "metrics": metrics})


# --- Stakeholders Directory ---
@app.route("/api/suppliers", methods=["GET"])
def list_suppliers():
    return jsonify({"success": True, "suppliers": [s.dict() for s in db.list_suppliers()]})


@app.route("/api/buyers", methods=["GET"])
def list_buyers():
    return jsonify({"success": True, "buyers": [b.dict() for b in db.list_buyers()]})


@app.route("/api/lenders", methods=["GET"])
def list_lenders():
    return jsonify({"success": True, "lenders": [l.dict() for l in db.list_lenders()]})


@app.route("/api/pos", methods=["GET"])
def list_pos():
    return jsonify({"success": True, "purchase_orders": [p.dict() for p in db.list_purchase_orders()]})


@app.route("/api/waybills", methods=["GET"])
def list_waybills():
    return jsonify({"success": True, "waybills": [w.dict() for w in db.list_waybills()]})


# --- Invoices & Autonomous Multi-Agent Pipeline ---
@app.route("/api/invoices", methods=["GET"])
def list_invoices():
    invoices = db.list_invoices()
    return jsonify({"success": True, "invoices": [inv.dict() for inv in invoices]})


@app.route("/api/invoices/<invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        return jsonify({"success": False, "error": "Invoice not found"}), 404
    return jsonify({"success": True, "invoice": invoice.dict()})


@app.route("/api/loans", methods=["GET"])
def list_loans():
    loans = db.list_loans()
    return jsonify({"success": True, "loans": [l.dict() for l in loans]})


@app.route("/api/loans/<loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = db.get_loan(loan_id)
    if not loan:
        return jsonify({"success": False, "error": "Loan not found"}), 404
    return jsonify({"success": True, "loan": loan.dict()})


@app.route("/api/invoices/ingest", methods=["POST"])
def ingest_and_audit_invoice():
    """Ingests invoice data or uploaded document and executes Antigravity Multi-Agent Audit."""
    data = request.get_json(silent=True) or {}

    if not data.get("invoice_number"):
        return jsonify({"success": False, "error": "invoice_number is required"}), 400

    # Ensure document exists in GCS Vault
    gcs_uri = data.get("gcs_uri")
    if not gcs_uri:
        filename = f"{data['invoice_number']}.pdf"
        mock_content = json.dumps(data, indent=2).encode("utf-8")
        doc_meta = cloud_storage.upload_document(filename, mock_content, "application/pdf")
        data["gcs_uri"] = doc_meta["gcs_uri"]
        data["file_sha256"] = doc_meta["sha256_checksum"]

    # Execute Autonomous Multi-Agent Team
    result = multi_agent_team.run_pipeline(data)
    return jsonify({"success": True, "result": result})


@app.route("/api/agents/run", methods=["POST"])
def trigger_agent_pipeline():
    """Directly triggers the Antigravity multi-agent audit on a custom invoice payload."""
    payload = request.get_json() or {}
    result = multi_agent_team.run_pipeline(payload)
    return jsonify({"success": True, "result": result})


# --- Human-In-The-Loop (HITL) Approval Gate ---
@app.route("/api/hitl/pending", methods=["GET"])
def get_pending_hitl():
    """Lists all loans requiring human credit officer sign-off."""
    pending = [l.dict() for l in db.list_loans() if l.approval_status == "ESCALATED_HITL"]
    return jsonify({"success": True, "count": len(pending), "pending_loans": pending})


@app.route("/api/hitl/decision", methods=["POST"])
def submit_hitl_decision():
    """Officer approves or rejects an escalated high-value or variance loan."""
    payload = request.get_json() or {}
    loan_id = payload.get("loan_id")
    decision = payload.get("decision")  # 'APPROVED' or 'REJECTED'
    officer_name = payload.get("officer_name", "Sarah Jenkins, Chief Credit Officer")
    officer_notes = payload.get("notes", "Compliance & logistics verified by human officer.")
    adjusted_ltv = payload.get("adjusted_ltv")

    loan = db.get_loan(loan_id)
    if not loan:
        return jsonify({"success": False, "error": f"Loan {loan_id} not found"}), 404

    if decision not in ("APPROVED", "REJECTED"):
        return jsonify({"success": False, "error": "Decision must be APPROVED or REJECTED"}), 400

    decision_record = {
        "decision": decision,
        "officer": officer_name,
        "notes": officer_notes,
        "decided_at": datetime.utcnow().isoformat() + "Z",
        "adjusted_ltv": adjusted_ltv
    }

    if decision == "APPROVED":
        loan.approval_status = "LENDER_APPROVED"
        # Select lender and disburse
        lenders = db.list_lenders()
        lender = lenders[0] if lenders else None
        if lender and loan.underwriting:
            disburse_amt = loan.underwriting.net_disbursement
            db.update_lender_deployment(lender.id, disburse_amt)
            loan.approval_status = "DISBURSED"
            loan.lender_id = lender.id
    else:
        loan.approval_status = "REJECTED"

    loan.hitl_decision = decision_record
    loan.updated_at = datetime.utcnow().isoformat() + "Z"
    db.add_loan(loan)

    # Record cryptographically chained audit block
    audit_block = db.record_audit_event(
        actor_agent=f"HUMAN_OFFICER:{officer_name}",
        action=f"HITL_{decision}_LOAN",
        entity_id=loan.id,
        payload={
            "loan_id": loan.id,
            "decision": decision,
            "officer_name": officer_name,
            "notes": officer_notes,
            "final_status": loan.approval_status,
            "disbursed_amount": loan.underwriting.net_disbursement if loan.approval_status == "DISBURSED" else 0.0
        }
    )

    cloud_pubsub.publish_event(
        event_type="HITL_DECISION_FINALIZED",
        payload={"loan_id": loan.id, "decision": decision, "status": loan.approval_status}
    )

    return jsonify({
        "success": True,
        "loan": loan.dict(),
        "audit_block_height": audit_block.block_height,
        "message": f"Loan {loan_id} {decision.lower()} successfully by {officer_name}."
    })


# --- Immutable Audit Trail & Regulatory Reporting ---
@app.route("/api/audit/chain", methods=["GET"])
def get_audit_chain():
    limit = int(request.args.get("limit", 100))
    chain = db.get_audit_trail(limit)
    return jsonify({"success": True, "total_blocks": len(db.audit_chain), "chain": [b.dict() for b in chain]})


@app.route("/api/audit/verify", methods=["GET"])
def verify_audit_integrity():
    verification = db.verify_audit_integrity()
    return jsonify({"success": True, "verification": verification})


@app.route("/api/audit/export", methods=["GET"])
def export_audit_package():
    """Generates complete regulatory audit bundle formatted for regulators (SEC/Basel III)."""
    verification = db.verify_audit_integrity()
    audit_data = {
        "regulatory_package": "AEROCREDITS_COMPLIANCE_AND_AUDIT_REPORT",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "governing_standard": "BASEL_III_SME_SUPPLY_CHAIN_FINANCE",
        "integrity_verification": verification,
        "system_metrics": db.get_metrics(),
        "total_audit_blocks": len(db.audit_chain),
        "audit_blocks": [b.dict() for b in db.audit_chain],
        "invoices": [inv.dict() for inv in db.list_invoices()],
        "loans": [l.dict() for l in db.list_loans()]
    }
    return jsonify(audit_data)


# --- Cloud Storage Vault Management ---
@app.route("/api/cloud/vault", methods=["GET"])
def get_cloud_vault_files():
    docs = cloud_storage.list_documents()
    return jsonify({"success": True, "bucket": GCS_BUCKET_INVOICES, "count": len(docs), "documents": docs})


if __name__ == "__main__":
    print(f"================================================================")
    print(f" AeroCredits: B2B Supply Chain Invoice Loan Engine")
    print(f" Autonomous Antigravity Multi-Agent Financial Audit Team")
    print(f" Running on http://{HOST}:{PORT}")
    print(f"================================================================")
    app.run(host=HOST, port=PORT, debug=DEBUG)
