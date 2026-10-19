"""
AeroCredits Launcher Script
B2B Supply Chain Invoice Loan Engine & Antigravity Multi-Agent Audit Team.
"""

import sys
import os

# Set root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app
from backend.config import PORT, HOST, DEBUG

if __name__ == "__main__":
    print("==================================================================")
    print("   AEROCREDITS: B2B SUPPLY CHAIN INVOICE LOAN ENGINE")
    print("   Enterprise Working Capital & Autonomous Multi-Agent FinTech")
    print(f"   Server running at: http://{HOST}:{PORT}")
    print("==================================================================")
    app.run(host=HOST, port=PORT, debug=DEBUG)
