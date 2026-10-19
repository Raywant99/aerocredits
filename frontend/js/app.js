/**
 * AeroCredits Main Frontend Application.
 * Coordinates dashboard metrics, persona switches, API interaction, and modals.
 */

const state = {
  activeTab: "supplier",
  metrics: {},
  suppliers: [],
  buyers: [],
  lenders: [],
  invoices: [],
  loans: [],
  pos: [],
  waybills: [],
  pendingHitl: [],
  activeAuditResult: null
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  setupNavigationTabs();
  setupModals();
  setupSampleButtons();
  loadAllData();

  // Polling for updates every 10 seconds
  setInterval(loadAllData, 10000);
});

// --- Tab Navigation ---
function setupNavigationTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const target = tab.dataset.target;
      state.activeTab = target;

      document.querySelectorAll(".tab-panel").forEach(panel => {
        panel.classList.remove("active");
      });
      const activePanel = document.getElementById(`panel-${target}`);
      if (activePanel) activePanel.classList.add("active");

      if (target === "audit") {
        renderAuditTrail();
      } else if (target === "agents") {
        if (state.invoices.length > 0 && !state.activeAuditResult) {
          selectInvoiceForVisualizer(state.invoices[0].id);
        }
      }
    });
  });
}

// --- Data Fetching ---
async function loadAllData() {
  try {
    const [metricsRes, suppRes, buyRes, lendRes, invRes, loanRes, poRes, wbRes, hitlRes] = await Promise.all([
      fetch("/api/metrics").then(r => r.json()),
      fetch("/api/suppliers").then(r => r.json()),
      fetch("/api/buyers").then(r => r.json()),
      fetch("/api/lenders").then(r => r.json()),
      fetch("/api/invoices").then(r => r.json()),
      fetch("/api/loans").then(r => r.json()),
      fetch("/api/pos").then(r => r.json()),
      fetch("/api/waybills").then(r => r.json()),
      fetch("/api/hitl/pending").then(r => r.json())
    ]);

    if (metricsRes.success) state.metrics = metricsRes.metrics;
    if (suppRes.success) state.suppliers = suppRes.suppliers;
    if (buyRes.success) state.buyers = buyRes.buyers;
    if (lendRes.success) state.lenders = lendRes.lenders;
    if (invRes.success) state.invoices = invRes.invoices;
    if (loanRes.success) state.loans = loanRes.loans;
    if (poRes.success) state.pos = poRes.purchase_orders;
    if (wbRes.success) state.waybills = wbRes.waybills;
    if (hitlRes.success) state.pendingHitl = hitlRes.pending_loans;

    renderMetrics();
    renderSupplierView();
    renderBuyerView();
    renderLenderView();
    renderHitlQueue();

    // Update HITL Badge Count
    const hitlBadge = document.getElementById("hitl-badge-count");
    if (hitlBadge) {
      hitlBadge.textContent = state.pendingHitl.length;
      hitlBadge.style.display = state.pendingHitl.length > 0 ? "inline-block" : "none";
    }

  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

// --- Render Top Metrics Banner ---
function renderMetrics() {
  const m = state.metrics;
  if (!m) return;

  const totalInvoicedEl = document.getElementById("metric-total-invoiced");
  const totalFinancedEl = document.getElementById("metric-total-financed");
  const autoRateEl = document.getElementById("metric-auto-rate");
  const liquidityEl = document.getElementById("metric-liquidity-pool");

  if (totalInvoicedEl) totalInvoicedEl.textContent = `$${(m.total_invoiced_value_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  if (totalFinancedEl) totalFinancedEl.textContent = `$${(m.total_financed_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  if (autoRateEl) autoRateEl.textContent = `${m.auto_approval_rate_percent || 0}%`;
  if (liquidityEl) liquidityEl.textContent = `$${(m.total_lender_available_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
}

// --- Render Supplier View ---
function renderSupplierView() {
  const tbody = document.getElementById("supplier-invoices-tbody");
  if (!tbody) return;

  if (state.invoices.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:2rem;">No invoices ingested yet. Click "Ingest New Invoice" to begin.</td></tr>`;
    return;
  }

  tbody.innerHTML = state.invoices.map(inv => {
    const loan = state.loans.find(l => l.invoice_id === inv.id);
    const status = loan ? loan.approval_status : "INGESTED";
    const statusClass = getStatusBadgeClass(status);
    const buyer = state.buyers.find(b => b.id === inv.buyer_id);
    const buyerName = buyer ? buyer.name : inv.buyer_id;

    return `
      <tr>
        <td><strong>${inv.invoice_number}</strong></td>
        <td>${buyerName}</td>
        <td>$${inv.total_amount.toLocaleString(undefined, {minimumFractionDigits: 2})} ${inv.currency}</td>
        <td>${inv.issue_date}</td>
        <td>${inv.due_date}</td>
        <td><span class="badge ${statusClass}">${formatStatus(status)}</span></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="viewAuditForInvoice('${inv.id}')">
            Audit Insights
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// --- Render Corporate Buyer View ---
function renderBuyerView() {
  const poTbody = document.getElementById("buyer-pos-tbody");
  const wbTbody = document.getElementById("buyer-waybills-tbody");

  if (poTbody) {
    poTbody.innerHTML = state.pos.map(po => {
      const buyer = state.buyers.find(b => b.id === po.buyer_id);
      return `
        <tr>
          <td><strong>${po.po_number}</strong></td>
          <td>${buyer ? buyer.name : po.buyer_id}</td>
          <td>$${po.total_authorized.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
          <td>${po.issue_date}</td>
          <td>${po.line_items.length} SKUs</td>
          <td><span class="badge badge-auto-approved">${po.status}</span></td>
        </tr>
      `;
    }).join("");
  }

  if (wbTbody) {
    wbTbody.innerHTML = state.waybills.map(wb => `
      <tr>
        <td><strong>${wb.waybill_number}</strong></td>
        <td>${wb.carrier}</td>
        <td>${wb.destination_facility}</td>
        <td>${wb.delivery_timestamp.split("T")[0]}</td>
        <td><span class="hash-pill">${wb.pod_hash.substring(0, 16)}...</span></td>
        <td><span class="badge badge-auto-approved">${wb.status}</span></td>
      </tr>
    `).join("");
  }
}

// --- Render Financial Lender View ---
function renderLenderView() {
  const container = document.getElementById("lender-pools-grid");
  if (!container) return;

  container.innerHTML = state.lenders.map(l => {
    const totalCap = l.available_capital + l.deployed_capital;
    const utilization = totalCap > 0 ? (l.deployed_capital / totalCap * 100).toFixed(1) : 0;
    return `
      <div class="content-card" style="margin-bottom:0;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
          <div>
            <h4 style="font-size:1.05rem; font-weight:700;">${l.name}</h4>
            <span style="font-size:0.75rem; color:var(--text-secondary);">${l.authorized_officer}</span>
          </div>
          <span class="badge badge-auto-approved">${l.risk_tolerance} RISK</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-bottom:1rem; font-size:0.85rem;">
          <div>
            <div style="color:var(--text-muted); font-size:0.75rem;">Available Liquidity</div>
            <div style="font-weight:700; color:var(--accent-green); font-size:1.1rem;">$${l.available_capital.toLocaleString()}</div>
          </div>
          <div>
            <div style="color:var(--text-muted); font-size:0.75rem;">Deployed Capital</div>
            <div style="font-weight:700; color:var(--accent-cyan); font-size:1.1rem;">$${l.deployed_capital.toLocaleString()}</div>
          </div>
        </div>
        <div style="background:var(--bg-secondary); border-radius:6px; height:8px; overflow:hidden; margin-bottom:0.5rem;">
          <div style="background:linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo)); width:${utilization}%; height:100%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted);">
          <span>Utilization: ${utilization}%</span>
          <span>Min APR: ${l.min_discount_rate_apr}%</span>
        </div>
      </div>
    `;
  }).join("");
}

// --- Render HITL Queue in Lender Tab ---
function renderHitlQueue() {
  const container = document.getElementById("hitl-queue-container");
  if (!container) return;

  if (state.pendingHitl.length === 0) {
    container.innerHTML = `
      <div style="background:var(--bg-secondary); border:1px dashed var(--border-color); border-radius:10px; padding:2rem; text-align:center; color:var(--text-muted);">
        <div style="font-size:1.5rem; margin-bottom:0.5rem;">🛡️</div>
        <strong>No Loans Currently in HITL Gate</strong>
        <p style="font-size:0.8rem; margin-top:0.25rem;">All incoming loans under $100k with 100% 3-way match are automatically approved. High-value or variance loans will appear here for human authorization.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.pendingHitl.map(loan => {
    const inv = state.invoices.find(i => i.id === loan.invoice_id) || {};
    const buyer = state.buyers.find(b => b.id === loan.buyer_id) || {};
    const supplier = state.suppliers.find(s => s.id === loan.supplier_id) || {};
    const uw = loan.underwriting || {};
    const rec = loan.reconciliation || {};

    return `
      <div class="hitl-alert-card">
        <div class="hitl-header">
          <div class="hitl-title">
            ⚠️ <span>High-Value Loan Approval Gate: ${inv.invoice_number || loan.invoice_id}</span>
          </div>
          <span class="badge badge-hitl">ESCALATED TO HUMAN CREDIT COMMITTEE</span>
        </div>
        <div class="hitl-body">
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:0.75rem; margin-bottom:0.85rem; background:rgba(0,0,0,0.25); padding:0.75rem; border-radius:8px;">
            <div>
              <span style="color:var(--text-muted); font-size:0.72rem; display:block;">Invoice Face Value</span>
              <strong style="font-size:1.1rem; color:#fff;">$${(loan.requested_amount || 0).toLocaleString(undefined, {minimumFractionDigits:2})}</strong>
            </div>
            <div>
              <span style="color:var(--text-muted); font-size:0.72rem; display:block;">Recommended Advance</span>
              <strong style="font-size:1.1rem; color:var(--accent-green);">$${(uw.net_disbursement || 0).toLocaleString(undefined, {minimumFractionDigits:2})} (${uw.recommended_ltv_percent || 85}% LTV)</strong>
            </div>
            <div>
              <span style="color:var(--text-muted); font-size:0.72rem; display:block;">3-Way Match Score</span>
              <strong style="font-size:1.1rem; color:${rec.line_item_score >= 95 ? 'var(--accent-green)' : 'var(--accent-amber)'};">${rec.line_item_score || 0}%</strong>
            </div>
            <div>
              <span style="color:var(--text-muted); font-size:0.72rem; display:block;">Counterparties</span>
              <span style="font-size:0.8rem; font-weight:600;">${supplier.name || loan.supplier_id} ➔ ${buyer.name || loan.buyer_id}</span>
            </div>
          </div>
          <div style="font-size:0.82rem; background:rgba(245, 158, 11, 0.08); border-left:3px solid var(--accent-amber); padding:0.5rem 0.75rem; margin-bottom:0.75rem;">
            <strong>Gatekeeper Reason:</strong> ${loan.hitl_reason || "Requires human authorization."}
          </div>
        </div>
        <div class="hitl-actions">
          <button class="btn btn-success" onclick="openHitlDecisionModal('${loan.id}', 'APPROVED')">
            ✅ Authorize & Disburse Loan
          </button>
          <button class="btn btn-outline" onclick="openHitlDecisionModal('${loan.id}', 'REJECTED')">
            ❌ Reject Loan
          </button>
          <button class="btn btn-outline" onclick="viewAuditForInvoice('${loan.invoice_id}')">
            🔍 Inspect Multi-Agent Evidence
          </button>
        </div>
      </div>
    `;
  }).join("");
}

// --- Helper Functions ---
function getStatusBadgeClass(status) {
  switch (status) {
    case "AUTO_APPROVED":
    case "DISBURSED":
    case "LENDER_APPROVED":
      return "badge-auto-approved";
    case "ESCALATED_HITL":
      return "badge-hitl";
    case "REJECTED":
      return "badge-rejected";
    default:
      return "badge-ingested";
  }
}

function formatStatus(status) {
  switch (status) {
    case "AUTO_APPROVED": return "⚡ Auto-Approved";
    case "DISBURSED": return "💸 Disbursed";
    case "LENDER_APPROVED": return "👤 Officer Approved";
    case "ESCALATED_HITL": return "⚠️ HITL Review Required";
    case "REJECTED": return "❌ Rejected";
    default: return "📥 Ingested";
  }
}

// --- Modals Setup ---
function setupModals() {
  // Ingest Modal
  const ingestBtn = document.getElementById("btn-open-ingest");
  const ingestModal = document.getElementById("modal-ingest-invoice");
  const closeIngest = document.getElementById("close-ingest-modal");

  if (ingestBtn && ingestModal) {
    ingestBtn.addEventListener("click", () => {
      ingestModal.classList.add("active");
    });
  }

  if (closeIngest && ingestModal) {
    closeIngest.addEventListener("click", () => {
      ingestModal.classList.remove("active");
    });
  }

  // HITL Decision Modal
  const hitlModal = document.getElementById("modal-hitl-decision");
  const closeHitl = document.getElementById("close-hitl-modal");
  if (closeHitl && hitlModal) {
    closeHitl.addEventListener("click", () => {
      hitlModal.classList.remove("active");
    });
  }

  // Invoice Ingestion Form Submission
  const form = document.getElementById("invoice-ingestion-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await submitInvoiceForAudit();
    });
  }
}

// --- Sample Buttons Setup ---
function setupSampleButtons() {
  const samples = {
    aerospace: {
      invoice_number: "INV-AERO-TURBINE-005",
      supplier_id: "supp_aerotech",
      buyer_id: "buy_boeing",
      po_number: "PO-BOEING-8821",
      waybill_number: "WB-FDX-77192",
      issue_date: "2026-10-15",
      due_date: "2026-12-15",
      currency: "USD",
      tax_rate: 0.08,
      gcs_uri: "gs://aerocredits-vault-inbound/INV-AERO-TURBINE-005.pdf",
      line_items: [
        {
          sku: "AERO-TURB-BLD-01",
          description: "Single-Crystal Nickel Alloy Turbine Blades Stage 1",
          ordered_quantity: 40.0,
          billed_quantity: 40.0,
          unit_price: 1960.0
        }
      ]
    },
    semiconductor: {
      invoice_number: "INV-NANO-WAFER-009",
      supplier_id: "supp_nanosilicon",
      buyer_id: "buy_nvidia",
      po_number: "PO-NVIDIA-5402",
      waybill_number: "WB-MSK-99014",
      issue_date: "2026-10-17",
      due_date: "2026-11-30",
      currency: "USD",
      tax_rate: 0.08,
      gcs_uri: "gs://aerocredits-vault-inbound/INV-NANO-WAFER-009.pdf",
      line_items: [
        {
          sku: "NANO-WAFER-300MM",
          description: "300mm High-Resistivity Float-Zone Silicon Substrates",
          ordered_quantity: 120.0,
          billed_quantity: 120.0,
          unit_price: 385.0
        }
      ]
    },
    heavy_hitl: {
      invoice_number: "INV-BOEING-HEAVY-012",
      supplier_id: "supp_aerotech",
      buyer_id: "buy_boeing",
      po_number: "PO-BOEING-HEAVY-9001",
      waybill_number: "WB-DHL-88120",
      issue_date: "2026-10-18",
      due_date: "2026-12-18",
      currency: "USD",
      tax_rate: 0.08,
      gcs_uri: "gs://aerocredits-vault-inbound/INV-BOEING-HEAVY-012.pdf",
      line_items: [
        {
          sku: "AERO-PROP-RING-88",
          description: "Titanium Structural Fan Containment Rings 110-inch",
          ordered_quantity: 2.0,
          billed_quantity: 2.0,
          unit_price: 122500.0
        }
      ]
    },
    variance: {
      invoice_number: "INV-BIO-VAR-007",
      supplier_id: "supp_biovax",
      buyer_id: "buy_pfizer",
      po_number: "PO-PFIZER-3310",
      waybill_number: "WB-BIO-3310-POD",
      issue_date: "2026-10-19",
      due_date: "2026-12-25",
      currency: "USD",
      tax_rate: 0.08,
      gcs_uri: "gs://aerocredits-vault-inbound/INV-BIO-VAR-007.pdf",
      line_items: [
        {
          sku: "BIO-CRYO-VIAL-500",
          description: "Ultra-Low Temp Nitrogen Cryo Storage Vials 2ml (Partial Delivery Variance)",
          ordered_quantity: 500.0,
          billed_quantity: 500.0,
          unit_price: 124.0
        }
      ]
    }
  };

  window.loadSample = function(key) {
    const s = samples[key];
    if (!s) return;

    document.getElementById("form-invoice-num").value = s.invoice_number;
    document.getElementById("form-supplier-id").value = s.supplier_id;
    document.getElementById("form-buyer-id").value = s.buyer_id;
    document.getElementById("form-po-num").value = s.po_number;
    document.getElementById("form-wb-num").value = s.waybill_number;
    document.getElementById("form-gcs-uri").value = s.gcs_uri;
    document.getElementById("form-items-json").value = JSON.stringify(s.line_items, null, 2);
  };
}

// --- Submit Invoice for Antigravity Multi-Agent Audit ---
async function submitInvoiceForAudit() {
  const invoiceNum = document.getElementById("form-invoice-num").value.trim();
  const supplierId = document.getElementById("form-supplier-id").value;
  const buyerId = document.getElementById("form-buyer-id").value;
  const poNum = document.getElementById("form-po-num").value.trim();
  const wbNum = document.getElementById("form-wb-num").value.trim();
  const gcsUri = document.getElementById("form-gcs-uri").value.trim();
  const itemsRaw = document.getElementById("form-items-json").value.trim();

  let lineItems = [];
  try {
    lineItems = JSON.parse(itemsRaw);
  } catch (e) {
    alert("Invalid JSON in line items field.");
    return;
  }

  const payload = {
    invoice_number: invoiceNum,
    supplier_id: supplierId,
    buyer_id: buyerId,
    po_number: poNum,
    waybill_number: wbNum,
    gcs_uri: gcsUri,
    currency: "USD",
    tax_rate: 0.08,
    line_items: lineItems
  };

  const submitBtn = document.getElementById("btn-submit-audit");
  submitBtn.disabled = true;
  submitBtn.innerHTML = "⏳ Antigravity Multi-Agent Team Auditing...";

  try {
    const res = await fetch("/api/invoices/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      document.getElementById("modal-ingest-invoice").classList.remove("active");
      await loadAllData();

      // Switch to AI Audit Room and display live audit execution
      state.activeAuditResult = data.result;
      document.querySelector('[data-target="agents"]').click();
      renderAgentRunResult(data.result);
    } else {
      alert("Error during audit: " + (data.error || "Unknown"));
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = "🚀 Launch Antigravity Multi-Agent Audit";
  }
}

// --- Open HITL Decision Modal ---
function openHitlDecisionModal(loanId, initialDecision = "APPROVED") {
  const loan = state.loans.find(l => l.id === loanId);
  if (!loan) return;

  const modal = document.getElementById("modal-hitl-decision");
  document.getElementById("hitl-modal-loan-id").value = loan.id;
  document.getElementById("hitl-modal-decision").value = initialDecision;
  document.getElementById("hitl-modal-loan-display").textContent = loan.id;
  document.getElementById("hitl-modal-amount-display").textContent = `$${loan.requested_amount.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  document.getElementById("hitl-modal-reason-display").textContent = loan.hitl_reason || "High value / variance threshold.";

  modal.classList.add("active");
}

// --- Submit HITL Decision ---
async function submitHitlDecision() {
  const loanId = document.getElementById("hitl-modal-loan-id").value;
  const decision = document.getElementById("hitl-modal-decision").value;
  const officerName = document.getElementById("hitl-modal-officer").value.trim();
  const notes = document.getElementById("hitl-modal-notes").value.trim();

  try {
    const res = await fetch("/api/hitl/decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        loan_id: loanId,
        decision: decision,
        officer_name: officerName,
        notes: notes
      })
    });

    const data = await res.json();
    if (data.success) {
      document.getElementById("modal-hitl-decision").classList.remove("active");
      await loadAllData();
      alert(`Decision recorded! Loan ${loanId} is now ${data.loan.approval_status}. Immutable Audit Block #${data.audit_block_height} added.`);
    } else {
      alert("Error submitting decision: " + data.error);
    }
  } catch (err) {
    alert("Error: " + err.message);
  }
}

// --- View Audit For Invoice ---
function viewAuditForInvoice(invoiceId) {
  document.querySelector('[data-target="agents"]').click();
  selectInvoiceForVisualizer(invoiceId);
}
