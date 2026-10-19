"""
AeroCredits Enterprise Seed Data.
Populates suppliers, Fortune 500 anchor buyers, financial lenders,
purchase orders (ERP), and logistics waybills.
"""

from backend.models.domain import (
    Supplier, Buyer, Lender, PurchaseOrder, LogisticsWaybill, InvoiceLineItem
)
from backend.models.database import db
from backend.agents.multi_agent_team import multi_agent_team


def load_seed_data():
    """Seeds the platform with enterprise market participants and logistics records."""

    # 1. Corporate Buyers (Anchors)
    buyers = [
        Buyer(
            id="buy_boeing",
            name="Boeing Defense, Space & Commercial Aviation",
            tax_id="US-EIN-91-0425693",
            country="United States",
            enterprise_tier="AAA",
            credit_score=980,
            payment_terms_days=60,
            total_credit_facility=50000000.0,
            active_utilized=4200000.0
        ),
        Buyer(
            id="buy_nvidia",
            name="Nvidia Semiconductor Systems Corp",
            tax_id="US-EIN-94-3177549",
            country="United States",
            enterprise_tier="AAA",
            credit_score=992,
            payment_terms_days=45,
            total_credit_facility=75000000.0,
            active_utilized=8100000.0
        ),
        Buyer(
            id="buy_pfizer",
            name="Pfizer Global Biopharma Supply",
            tax_id="US-EIN-13-5315170",
            country="United States",
            enterprise_tier="AA+",
            credit_score=945,
            payment_terms_days=90,
            total_credit_facility=40000000.0,
            active_utilized=3500000.0
        )
    ]
    for b in buyers:
        db.add_buyer(b)

    # 2. Suppliers
    suppliers = [
        Supplier(
            id="supp_aerotech",
            name="AeroTech Precision Turbine Dynamics Inc.",
            tax_id="US-EIN-45-8910291",
            country="United States",
            industry="Aerospace & Defense Precision Machining",
            credit_rating="A+",
            kyc_status="VERIFIED",
            bank_account="JPMC-ACC-99214018-USD",
            credit_limit=5000000.0,
            utilized_limit=125000.0
        ),
        Supplier(
            id="supp_nanosilicon",
            name="NanoSilicon High-Purity Substrates LLC",
            tax_id="US-EIN-88-2940182",
            country="United States",
            industry="Advanced Semiconductor Fabrication",
            credit_rating="AA",
            kyc_status="VERIFIED",
            bank_account="CITI-ACC-33019284-USD",
            credit_limit=8000000.0,
            utilized_limit=46200.0
        ),
        Supplier(
            id="supp_biovax",
            name="BioVax Cold-Chain Packaging Systems",
            tax_id="US-EIN-62-1049281",
            country="United States",
            industry="Pharmaceutical Logistics & Cryogenics",
            credit_rating="A",
            kyc_status="VERIFIED",
            bank_account="BOFA-ACC-77401923-USD",
            credit_limit=3000000.0,
            utilized_limit=0.0
        )
    ]
    for s in suppliers:
        db.add_supplier(s)

    # 3. Financial Lenders (Institutional Liquidity Pools)
    lenders = [
        Lender(
            id="lender_001",
            name="Apex Commercial Liquidity Corp",
            available_capital=12500000.0,
            deployed_capital=2450000.0,
            min_discount_rate_apr=7.25,
            risk_tolerance="BALANCED",
            authorized_officer="Sarah Jenkins, Chief Credit Officer"
        ),
        Lender(
            id="lender_002",
            name="Vertex Supply Chain Private Credit Fund",
            available_capital=8200000.0,
            deployed_capital=1800000.0,
            min_discount_rate_apr=7.80,
            risk_tolerance="GROWTH",
            authorized_officer="Marcus Vance, Managing Director"
        ),
        Lender(
            id="lender_003",
            name="Horizon Global Structured Receivables",
            available_capital=15000000.0,
            deployed_capital=3200000.0,
            min_discount_rate_apr=6.95,
            risk_tolerance="CONSERVATIVE",
            authorized_officer="Elena Rostova, Head of Underwriting"
        )
    ]
    for l in lenders:
        db.add_lender(l)

    # 4. ERP Purchase Orders
    pos = [
        # PO 1: Boeing - Turbine Blades ($78,400)
        PurchaseOrder(
            po_number="PO-BOEING-8821",
            buyer_id="buy_boeing",
            supplier_id="supp_aerotech",
            issue_date="2026-09-10",
            total_authorized=78400.0,
            currency="USD",
            line_items=[
                InvoiceLineItem(
                    item_id="po_item_1",
                    sku="AERO-TURB-BLD-01",
                    description="Single-Crystal Nickel Alloy Turbine Blades Stage 1",
                    ordered_quantity=40.0,
                    billed_quantity=40.0,
                    unit_price=1960.0,
                    line_total=78400.0,
                    hs_code="8411.91.00"
                )
            ]
        ),
        # PO 2: Nvidia - Silicon Substrates ($46,200)
        PurchaseOrder(
            po_number="PO-NVIDIA-5402",
            buyer_id="buy_nvidia",
            supplier_id="supp_nanosilicon",
            issue_date="2026-09-18",
            total_authorized=46200.0,
            currency="USD",
            line_items=[
                InvoiceLineItem(
                    item_id="po_item_2",
                    sku="NANO-WAFER-300MM",
                    description="300mm High-Resistivity Float-Zone Silicon Substrates",
                    ordered_quantity=120.0,
                    billed_quantity=120.0,
                    unit_price=385.0,
                    line_total=46200.0,
                    hs_code="3818.00.10"
                )
            ]
        ),
        # PO 3: Boeing - Heavy Propulsion Ring Casings ($245,000) -> High Value HITL Case!
        PurchaseOrder(
            po_number="PO-BOEING-HEAVY-9001",
            buyer_id="buy_boeing",
            supplier_id="supp_aerotech",
            issue_date="2026-09-22",
            total_authorized=245000.0,
            currency="USD",
            line_items=[
                InvoiceLineItem(
                    item_id="po_item_3",
                    sku="AERO-PROP-RING-88",
                    description="Titanium Structural Fan Containment Rings 110-inch",
                    ordered_quantity=2.0,
                    billed_quantity=2.0,
                    unit_price=122500.0,
                    line_total=245000.0,
                    hs_code="8411.91.90"
                )
            ]
        ),
        # PO 4: Pfizer - Cryo Vials ($62,000) -> Discrepancy Case!
        PurchaseOrder(
            po_number="PO-PFIZER-3310",
            buyer_id="buy_pfizer",
            supplier_id="supp_biovax",
            issue_date="2026-09-25",
            total_authorized=62000.0,
            currency="USD",
            line_items=[
                InvoiceLineItem(
                    item_id="po_item_4",
                    sku="BIO-CRYO-VIAL-500",
                    description="Ultra-Low Temp Nitrogen Cryo Storage Vials 2ml",
                    ordered_quantity=500.0,
                    billed_quantity=500.0,
                    unit_price=124.0,
                    line_total=62000.0,
                    hs_code="3923.30.00"
                )
            ]
        )
    ]
    for p in pos:
        db.add_purchase_order(p)

    # 5. Logistics Waybills / Goods Receipt Notes (GRN)
    waybills = [
        # WB 1: FedEx Freight for Turbine Blades (Delivered 40/40)
        LogisticsWaybill(
            waybill_number="WB-FDX-77192",
            carrier="FedEx Freight Priority",
            tracking_number="FDX-8820-9912",
            origin_hub="Cincinnati Northern Kentucky Air Cargo Hub",
            destination_facility="Boeing Commercial Airplanes - Renton Delivery Center",
            delivery_timestamp="2026-09-15T14:30:00Z",
            delivered_quantities={"AERO-TURB-BLD-01": 40.0},
            recipient_signoff="D. Miller, Boeing Quality Assurance Mgr",
            pod_hash="4a8b7c29e1d84f28a9c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5",
            status="DELIVERED_VERIFIED"
        ),
        # WB 2: Maersk Logistics for Silicon Substrates (Delivered 120/120)
        LogisticsWaybill(
            waybill_number="WB-MSK-99014",
            carrier="Maersk Specialized Tech Logistics",
            tracking_number="MSK-5541-0023",
            origin_hub="Port of Oakland Air Cargo Gateway",
            destination_facility="Nvidia System Integration Facility - Santa Clara",
            delivery_timestamp="2026-09-21T09:15:00Z",
            delivered_quantities={"NANO-WAFER-300MM": 120.0},
            recipient_signoff="K. Tanaka, Nvidia Inbound Logistics Inspector",
            pod_hash="9f8e7d6c5b4a3928172635445362718293049586718293a4b5c6d7e8f9a0b1c2",
            status="DELIVERED_VERIFIED"
        ),
        # WB 3: DHL Heavy Freight for Titanium Ring Casings (Delivered 2/2)
        LogisticsWaybill(
            waybill_number="WB-DHL-88120",
            carrier="DHL Global Heavy Lift",
            tracking_number="DHL-9940-1123",
            origin_hub="Seattle-Tacoma Heavy Freight Intermodal Terminal",
            destination_facility="Boeing Everett Final Assembly Facility",
            delivery_timestamp="2026-09-28T16:45:00Z",
            delivered_quantities={"AERO-PROP-RING-88": 2.0},
            recipient_signoff="J. Reynolds, Boeing Assembly Operations Lead",
            pod_hash="112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00",
            status="DELIVERED_VERIFIED"
        ),
        # WB 4: BioVax Cold-Chain (Delivered only 450 out of 500! Variance!)
        LogisticsWaybill(
            waybill_number="WB-BIO-3310-POD",
            carrier="World Courier Pharma Cold-Chain",
            tracking_number="WC-3391-7788",
            origin_hub="Philadelphia Life Sciences Cargo Depot",
            destination_facility="Pfizer Sterile Injectable Manufacturing - Kalamazoo",
            delivery_timestamp="2026-09-30T11:20:00Z",
            delivered_quantities={"BIO-CRYO-VIAL-500": 450.0},  # 50 shortfall!
            recipient_signoff="R. Chen, Pfizer Inbound Receiving Inspector (Partial Delivery Noted)",
            pod_hash="aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
            status="DELIVERED_VERIFIED"
        )
    ]
    for w in waybills:
        db.add_waybill(w)

    # 6. Run initial autonomous multi-agent pipeline on sample invoices to seed real transactions!
    # Invoice A: Turbine Blades (Value $84,672 total incl tax -> < $100k -> AUTO APPROVED)
    multi_agent_team.run_pipeline({
        "invoice_number": "INV-AERO-2026-01",
        "supplier_id": "supp_aerotech",
        "buyer_id": "buy_boeing",
        "po_number": "PO-BOEING-8821",
        "waybill_number": "WB-FDX-77192",
        "issue_date": "2026-09-12",
        "due_date": "2026-11-12",
        "currency": "USD",
        "tax_rate": 0.08,
        "gcs_uri": "gs://aerocredits-vault-inbound/INV-AERO-2026-01.pdf",
        "line_items": [
            {
                "sku": "AERO-TURB-BLD-01",
                "description": "Single-Crystal Nickel Alloy Turbine Blades Stage 1",
                "ordered_quantity": 40.0,
                "billed_quantity": 40.0,
                "unit_price": 1960.0
            }
        ]
    })

    # Invoice B: Silicon Substrates (Value $49,896 total incl tax -> < $100k -> AUTO APPROVED)
    multi_agent_team.run_pipeline({
        "invoice_number": "INV-NANO-2026-02",
        "supplier_id": "supp_nanosilicon",
        "buyer_id": "buy_nvidia",
        "po_number": "PO-NVIDIA-5402",
        "waybill_number": "WB-MSK-99014",
        "issue_date": "2026-09-20",
        "due_date": "2026-11-04",
        "currency": "USD",
        "tax_rate": 0.08,
        "gcs_uri": "gs://aerocredits-vault-inbound/INV-NANO-2026-02.pdf",
        "line_items": [
            {
                "sku": "NANO-WAFER-300MM",
                "description": "300mm High-Resistivity Float-Zone Silicon Substrates",
                "ordered_quantity": 120.0,
                "billed_quantity": 120.0,
                "unit_price": 385.0
            }
        ]
    })

    # Invoice C: Titanium Containment Rings (Value $264,600 total incl tax -> >= $100k -> ESCALATED TO HITL GATE!)
    multi_agent_team.run_pipeline({
        "invoice_number": "INV-AERO-HEAVY-03",
        "supplier_id": "supp_aerotech",
        "buyer_id": "buy_boeing",
        "po_number": "PO-BOEING-HEAVY-9001",
        "waybill_number": "WB-DHL-88120",
        "issue_date": "2026-09-26",
        "due_date": "2026-11-26",
        "currency": "USD",
        "tax_rate": 0.08,
        "gcs_uri": "gs://aerocredits-vault-inbound/INV-AERO-HEAVY-03.pdf",
        "line_items": [
            {
                "sku": "AERO-PROP-RING-88",
                "description": "Titanium Structural Fan Containment Rings 110-inch",
                "ordered_quantity": 2.0,
                "billed_quantity": 2.0,
                "unit_price": 122500.0
            }
        ]
    })

    print("[Seed Data] Enterprise market data, logistics records, and initial audited loans loaded successfully.")
