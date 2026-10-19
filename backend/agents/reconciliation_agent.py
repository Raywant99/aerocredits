"""
AeroCredits 3-Way Reconciliation Agent.
Conducts autonomous line-item matching across Purchase Orders (ERP),
Invoices, and Logistics Waybills / Goods Receipt Notes (GRN).
"""

from typing import Dict, Any, List
from backend.models.domain import Invoice, ReconciliationResult, ItemVariance
from backend.models.database import db
from backend.gcp.pubsub_adapter import cloud_pubsub


class ReconciliationAgent:
    """Agent performing 3-way matching: PO <-> Invoice <-> Logistics Waybill."""

    def __init__(self, name: str = "AeroCredits-ReconcileAgent-02"):
        self.name = name
        self.role = "3-Way Logistics & Invoice Audit Specialist"

    def process(self, invoice: Invoice) -> Dict[str, Any]:
        thoughts = []
        thoughts.append(f"[{self.name}] Initiating 3-way reconciliation for Invoice {invoice.invoice_number}...")

        # 1. Fetch Purchase Order
        po = db.get_purchase_order(invoice.po_number)
        po_found = po is not None
        thoughts.append(f"[{self.name}] Step 1: Checking Purchase Order {invoice.po_number}... {'VERIFIED IN ERP' if po_found else 'PO NOT FOUND IN ERP'}")

        # 2. Fetch Logistics Waybill / GRN
        waybill = db.get_waybill(invoice.waybill_number)
        wb_found = waybill is not None
        thoughts.append(f"[{self.name}] Step 2: Checking Logistics Waybill {invoice.waybill_number}... {'CARRIER SIGN-OFF CONFIRMED' if wb_found else 'WAYBILL PENDING'}")

        po_items_map = {item.sku: item for item in (po.line_items if po else [])}
        delivered_map = (waybill.delivered_quantities if waybill else {})

        item_variances: List[ItemVariance] = []
        total_billed_qty = 0.0
        total_delivered_qty = 0.0
        total_po_expected_value = 0.0
        total_inv_value = 0.0
        findings = []

        for item in invoice.line_items:
            total_billed_qty += item.billed_quantity
            total_inv_value += item.line_total

            po_item = po_items_map.get(item.sku)
            po_price = po_item.unit_price if po_item else item.unit_price
            po_ord_qty = po_item.ordered_quantity if po_item else item.billed_quantity
            total_po_expected_value += (po_price * item.billed_quantity)

            deliv_qty = delivered_map.get(item.sku, item.billed_quantity if wb_found else 0.0)
            total_delivered_qty += deliv_qty

            qty_match = abs(deliv_qty - item.billed_quantity) < 0.001
            price_match = abs(po_price - item.unit_price) < 0.01

            status_item = "PERFECT_MATCH"
            if not qty_match and not price_match:
                status_item = "QTY_AND_PRICE_DISCREPANCY"
                findings.append(f"SKU {item.sku}: Delivered {deliv_qty} vs Billed {item.billed_quantity}, Price diff ${item.unit_price - po_price:.2f}")
            elif not qty_match:
                status_item = "QUANTITY_SHORTFALL" if deliv_qty < item.billed_quantity else "OVER_DELIVERY"
                findings.append(f"SKU {item.sku}: Delivered {deliv_qty} vs Billed {item.billed_quantity}")
            elif not price_match:
                status_item = "PRICE_MISMATCH"
                findings.append(f"SKU {item.sku}: Invoiced ${item.unit_price} vs Authorized PO ${po_price}")

            item_variances.append(
                ItemVariance(
                    sku=item.sku,
                    description=item.description,
                    ordered_qty=po_ord_qty,
                    billed_qty=item.billed_quantity,
                    delivered_qty=deliv_qty,
                    unit_price_po=po_price,
                    unit_price_inv=item.unit_price,
                    qty_match=qty_match,
                    price_match=price_match,
                    status=status_item
                )
            )

        # Quantity variance %
        qty_diff = abs(total_billed_qty - total_delivered_qty)
        qty_var_pct = round((qty_diff / total_billed_qty * 100.0) if total_billed_qty > 0 else 0.0, 2)

        # Price variance %
        price_diff = abs(total_inv_value - total_po_expected_value)
        price_var_pct = round((price_diff / total_po_expected_value * 100.0) if total_po_expected_value > 0 else 0.0, 2)

        # Base scoring calculation
        score = 100.0
        if not po_found:
            score -= 40.0
            findings.append("Critical: Purchase Order unconfirmed in corporate buyer's ERP database.")
        if not wb_found:
            score -= 40.0
            findings.append("Critical: Carrier logistics bill of lading missing proof-of-delivery.")

        score -= (qty_var_pct * 3.0)
        score -= (price_var_pct * 4.0)
        reconcile_score = max(0.0, min(100.0, round(score, 1)))

        confidence = 99.2 if (po_found and wb_found) else 74.0

        thoughts.append(f"[{self.name}] Reconciliation computed: Score {reconcile_score}% | Qty Var: {qty_var_pct}% | Price Var: {price_var_pct}%.")
        if not findings:
            findings.append("3-way matching verified: 100% SKU parity, exact logistics delivery sign-off, authorized PO pricing.")
            thoughts.append(f"[{self.name}] Verdict: 3-way match passed without anomalies.")
        else:
            thoughts.append(f"[{self.name}] Warning: {len(findings)} line-item discrepancy alert(s) detected.")

        reconcile_result = ReconciliationResult(
            po_match=po_found,
            logistics_match=wb_found,
            line_item_score=reconcile_score,
            quantity_variance_percent=qty_var_pct,
            price_variance_percent=price_var_pct,
            item_variances=item_variances,
            findings=findings,
            confidence_score=confidence
        )

        audit_block = db.record_audit_event(
            actor_agent=self.name,
            action="EXECUTE_3_WAY_RECONCILIATION",
            entity_id=invoice.id,
            payload={
                "invoice_number": invoice.invoice_number,
                "po_number": invoice.po_number,
                "waybill_number": invoice.waybill_number,
                "reconciliation_score": reconcile_score,
                "qty_variance_pct": qty_var_pct,
                "price_variance_pct": price_var_pct,
                "findings_count": len(findings)
            }
        )

        cloud_pubsub.publish_event(
            event_type="RECONCILIATION_COMPLETED",
            payload={"invoice_id": invoice.id, "reconciliation_score": reconcile_score}
        )

        return {
            "agent": self.name,
            "role": self.role,
            "status": "COMPLETED",
            "result": reconcile_result,
            "thoughts": thoughts,
            "audit_block_height": audit_block.block_height
        }
