"""
AeroCredits System Configuration
Thresholds, Google Cloud Settings, and Antigravity SDK Parameters.
"""

import os

# Financial & Risk Thresholds
HITL_LOAN_THRESHOLD_USD = float(os.environ.get("AEROCREDITS_HITL_THRESHOLD", "100000.0"))
MIN_RECONCILIATION_SCORE_FOR_AUTO_APPROVAL = 95.0
MAX_ALLOWED_QUANTITY_VARIANCE_PCT = 1.0
MAX_ALLOWED_PRICE_VARIANCE_PCT = 0.5
DEFAULT_ADVANCE_RATE_LTV = 85.0  # 85% advance of verified invoice
BENCHMARK_INTEREST_RATE_APR = 4.75  # Base SOFR rate
MIN_LENDER_SPREAD_APR = 2.50       # Minimum risk spread

# Google Cloud & Storage Configuration
GCP_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "aerocredits-enterprise-cloud")
GCP_REGION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
GCS_BUCKET_INVOICES = os.environ.get("GCS_BUCKET_INVOICES", "aerocredits-vault-inbound")
GCS_BUCKET_AUDIT = os.environ.get("GCS_BUCKET_AUDIT", "aerocredits-vault-audit")
PUBSUB_TOPIC_INVOICE_EVENTS = "projects/aerocredits-enterprise-cloud/topics/invoice-events"

# Antigravity SDK Configuration
ANTIGRAVITY_MODEL = os.environ.get("ANTIGRAVITY_MODEL", "gemini-3.8-flash")
USE_LIVE_VERTEX = bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GEMINI_API_KEY"))

# Server Configuration
PORT = int(os.environ.get("PORT", "5055"))
HOST = os.environ.get("HOST", "127.0.0.1")
DEBUG = True
