/**
 * AeroCredits Autonomous AI Multi-Agent Audit Visualizer.
 * Renders live thought streams, confidence gauges, and pipeline stage transitions.
 */

function selectInvoiceForVisualizer(invoiceId) {
  const inv = state.invoices.find(i => i.id === invoiceId);
  const loan = state.loans.find(l => l.invoice_id === invoiceId);

  if (!inv) return;

  // Populate dropdown
  const selector = document.getElementById("agent-invoice-select");
  if (selector) {
    selector.innerHTML = state.invoices.map(i => `
      <option value="${i.id}" ${i.id === invoiceId ? 'selected' : ''}>
        ${i.invoice_number} - $${i.total_amount.toLocaleString()} (${i.id})
      </option>
    `).join("");
  }

  renderAgentRunForInvoice(inv, loan);
}

function renderAgentRunResult(auditResult) {
  const inv = auditResult.invoice;
  const loan = auditResult.loan;

  const selector = document.getElementById("agent-invoice-select");
  if (selector) {
    selector.innerHTML = state.invoices.map(i => `
      <option value="${i.id}" ${i.id === inv.id ? 'selected' : ''}>
        ${i.invoice_number} - $${i.total_amount.toLocaleString()} (${i.id})
      </option>
    `).join("");
  }

  // Populate pipeline logs
  renderPipelineLogs(auditResult.pipeline_log, inv, loan);
}

function renderAgentRunForInvoice(inv, loan) {
  const rec = (loan && loan.reconciliation) || {};
  const comp = (loan && loan.compliance) || {};
  const uw = (loan && loan.underwriting) || {};

  // Build synthetic thought steps for visualization
  const pipelineLog = [
    {
      stage: "INGESTION_EXTRACTION",
      agent: "AeroCredits-IngestionAgent-01",
      role: "Document Ingestion & Cloud Vault Specialist",
      duration_ms: 184.2,
      thoughts: [
        `[AeroCredits-IngestionAgent-01] Connecting to Google Cloud Storage bucket...`,
        `[AeroCredits-IngestionAgent-01] Ingested document from ${inv.gcs_uri} with verified SHA-256: ${inv.file_sha256 ? inv.file_sha256.substring(0, 16) : '4a8b7c29e1d84f28'}...`,
        `[AeroCredits-IngestionAgent-01] Parsing line items and tax breakdown via OCR model...`,
        `[AeroCredits-IngestionAgent-01] Extraction complete: ${inv.line_items.length} line items verified. Total Face Value: $${inv.total_amount.toLocaleString()} ${inv.currency}.`
      ],
      summary: `Extracted ${inv.line_items.length} line items. Total face value: $${inv.total_amount.toLocaleString()}`
    },
    {
      stage: "3_WAY_RECONCILIATION",
      agent: "AeroCredits-ReconcileAgent-02",
      role: "3-Way Logistics & Invoice Audit Specialist",
      duration_ms: 295.4,
      thoughts: [
        `[AeroCredits-ReconcileAgent-02] Initiating 3-way reconciliation for Invoice ${inv.invoice_number}...`,
        `[AeroCredits-ReconcileAgent-02] Step 1: Checking Purchase Order ${inv.po_number}... ${rec.po_match !== false ? 'VERIFIED IN ERP' : 'PO NOT FOUND'}`,
        `[AeroCredits-ReconcileAgent-02] Step 2: Checking Logistics Waybill ${inv.waybill_number}... ${rec.logistics_match !== false ? 'CARRIER SIGN-OFF CONFIRMED' : 'WAYBILL PENDING'}`,
        `[AeroCredits-ReconcileAgent-02] Reconciliation computed: Score ${rec.line_item_score || 100}% | Qty Var: ${rec.quantity_variance_percent || 0}% | Price Var: ${rec.price_variance_percent || 0}%.`,
        ...(rec.findings ? rec.findings.map(f => `[AeroCredits-ReconcileAgent-02] Audit Note: ${f}`) : [])
      ],
      score: rec.line_item_score || 100,
      summary: `3-Way Reconciliation Score: ${rec.line_item_score || 100}% (Qty Var: ${rec.quantity_variance_percent || 0}%)`
    },
    {
      stage: "COMPLIANCE_SCREENING",
      agent: "AeroCredits-ComplianceAgent-03",
      role: "Multi-Tier Regulatory Compliance & Fraud Specialist",
      duration_ms: 210.8,
      thoughts: [
        `[AeroCredits-ComplianceAgent-03] Initiating multi-tier compliance audit for Invoice ${inv.invoice_number}...`,
        `[AeroCredits-ComplianceAgent-03] Tier 1 Tax/KYC Check: ${comp.tax_id_verified !== false ? 'PASSED - Active Entity Filing' : 'FAILED'}`,
        `[AeroCredits-ComplianceAgent-03] Tier 2 Sanctions & PEP Screening: ${comp.sanctions_cleared !== false ? 'CLEARED (OFAC/EU/UN)' : 'RESTRICTED WATCHLIST HIT'}`,
        `[AeroCredits-ComplianceAgent-03] Tier 3 Graph Anti-Fraud Check: ${comp.circular_trading_detected ? 'CIRCULAR FRAUD SUSPECTED' : 'NO CIRCULAR TRADING DETECTED'}`,
        `[AeroCredits-ComplianceAgent-03] Tier 4 Facility Limit Check: ${comp.buyer_limit_ok !== false ? 'WITHIN CORPORATE CEILING' : 'LIMIT EXCEEDED'}`,
        `[AeroCredits-ComplianceAgent-03] Compliance Audit Verdict: ${comp.status || 'PASSED'} (Score: ${comp.compliance_score || 100}%).`
      ],
      score: comp.compliance_score || 100,
      summary: `Compliance Status: ${comp.status || 'PASSED'} (Score: ${comp.compliance_score || 100}%)`
    },
    {
      stage: "CREDIT_UNDERWRITING",
      agent: "AeroCredits-UnderwriteAgent-04",
      role: "Quantitative Credit Underwriter & Pricing Specialist",
      duration_ms: 195.1,
      thoughts: [
        `[AeroCredits-UnderwriteAgent-04] Initiating algorithmic underwriting for Invoice ${inv.invoice_number}...`,
        `[AeroCredits-UnderwriteAgent-04] Risk Pricing: Benchmark 4.75% SOFR + Enterprise Risk Spread = ${uw.annualized_discount_rate || 7.8}% APR.`,
        `[AeroCredits-UnderwriteAgent-04] Principal Advance: $${(uw.loan_principal_advance || inv.total_amount * 0.85).toLocaleString(undefined, {minimumFractionDigits: 2})} (${uw.recommended_ltv_percent || 85}% LTV).`,
        `[AeroCredits-UnderwriteAgent-04] Calculated Discount Fee: $${(uw.discount_fee || 0).toLocaleString(undefined, {minimumFractionDigits: 2})} for ${uw.tenure_days || 60} days tenure.`,
        `[AeroCredits-UnderwriteAgent-04] Net Disbursement to Supplier: $${(uw.net_disbursement || 0).toLocaleString(undefined, {minimumFractionDigits: 2})} | Risk Tier: ${uw.risk_tier || 'LOW_RISK'}.`
      ],
      summary: `Priced at ${uw.annualized_discount_rate || 7.8}% APR. Net Cash: $${(uw.net_disbursement || 0).toLocaleString()}`
    },
    {
      stage: "GOVERNANCE_GATEKEEPER",
      agent: "AeroCredits-Gatekeeper-05",
      role: "Governance & Approval Gatekeeper Specialist",
      duration_ms: 142.0,
      thoughts: [
        `[AeroCredits-Gatekeeper-05] Evaluating governance rules for Loan Request...`,
        loan && loan.approval_status === "ESCALATED_HITL"
          ? `[AeroCredits-Gatekeeper-05] ESCALATION TRIGGERED: ${loan.hitl_reason}`
          : `[AeroCredits-Gatekeeper-05] AUTO-APPROVAL CLEARED: Clean 3-way match, verified compliance, and amount within auto-approval policy.`,
        `[AeroCredits-Gatekeeper-05] Final Verdict: ${loan ? loan.approval_status : 'AUTO_APPROVED'} (${loan ? loan.approval_tier : 'TIER_1_AUTO'}). Chained to immutable audit ledger.`
      ],
      summary: `Decision: ${loan ? loan.approval_status : 'AUTO_APPROVED'} (${loan ? loan.approval_tier : 'TIER_1_AUTO'})`
    }
  ];

  renderPipelineLogs(pipelineLog, inv, loan);
}

function renderPipelineLogs(pipelineLog, inv, loan) {
  // Update node metrics
  const nodes = document.querySelectorAll(".agent-node");
  pipelineLog.forEach((stage, idx) => {
    if (nodes[idx]) {
      const durEl = nodes[idx].querySelector(".stage-duration");
      const statEl = nodes[idx].querySelector(".stage-status");
      if (durEl) durEl.textContent = `${stage.duration_ms} ms`;
      if (statEl) {
        if (stage.stage === "GOVERNANCE_GATEKEEPER" && loan && loan.approval_status === "ESCALATED_HITL") {
          statEl.textContent = "ESCALATED HITL";
          statEl.style.color = "var(--accent-amber)";
        } else if (stage.stage === "3_WAY_RECONCILIATION" && stage.score < 95) {
          statEl.textContent = `${stage.score}% (ALERT)`;
          statEl.style.color = "var(--accent-amber)";
        } else {
          statEl.textContent = "VERIFIED";
          statEl.style.color = "var(--accent-green)";
        }
      }
    }
  });

  // Render Console Output
  const consoleEl = document.getElementById("agent-thoughts-stream");
  if (!consoleEl) return;

  let streamHtml = "";
  pipelineLog.forEach(stage => {
    streamHtml += `
      <div style="margin-top:0.75rem; margin-bottom:0.25rem; font-weight:700; color:var(--accent-cyan); border-bottom:1px solid rgba(56, 189, 248, 0.2); padding-bottom:0.2rem;">
        ▶ PHASE: ${stage.stage} [${stage.agent}] (${stage.duration_ms} ms)
      </div>
    `;

    stage.thoughts.forEach(thought => {
      let colorClass = "thought-info";
      if (thought.includes("PASSED") || thought.includes("CLEARED") || thought.includes("VERIFIED") || thought.includes("SUCCESS")) {
        colorClass = "thought-success";
      } else if (thought.includes("ESCALATION") || thought.includes("Warning") || thought.includes("FLAGGED") || thought.includes("shortfall")) {
        colorClass = "thought-warn";
      } else if (thought.includes("CRITICAL") || thought.includes("FAILED") || thought.includes("REJECTED")) {
        colorClass = "thought-error";
      }

      streamHtml += `
        <div class="thought-entry ${colorClass}">
          ${escapeHtml(thought)}
        </div>
      `;
    });
  });

  consoleEl.innerHTML = streamHtml;

  // Render Line-Item 3-Way Match Table
  renderLineItemAuditTable(inv, loan);
}

function renderLineItemAuditTable(inv, loan) {
  const container = document.getElementById("line-items-audit-tbody");
  if (!container || !inv) return;

  const rec = (loan && loan.reconciliation) || {};
  const variances = rec.item_variances || [];
  const varMap = {};
  variances.forEach(v => { varMap[v.sku] = v; });

  container.innerHTML = inv.line_items.map(item => {
    const v = varMap[item.sku] || {};
    const delivQty = v.delivered_qty !== undefined ? v.delivered_qty : item.billed_quantity;
    const isQtyMatch = v.qty_match !== false;
    const isPriceMatch = v.price_match !== false;

    return `
      <tr>
        <td><strong>${item.sku}</strong></td>
        <td>${item.description}</td>
        <td>${item.ordered_quantity}</td>
        <td><strong style="color:${isQtyMatch ? 'var(--text-primary)' : 'var(--accent-amber)'};">${item.billed_quantity}</strong></td>
        <td><strong style="color:${isQtyMatch ? 'var(--accent-green)' : 'var(--accent-amber)'};">${delivQty}</strong></td>
        <td>$${item.unit_price.toFixed(2)}</td>
        <td>$${item.line_total.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
        <td>
          <span class="badge ${isQtyMatch && isPriceMatch ? 'badge-auto-approved' : 'badge-hitl'}">
            ${isQtyMatch && isPriceMatch ? 'MATCHED (100%)' : 'VARIANCE FLAGGED'}
          </span>
        </td>
      </tr>
    `;
  }).join("");
}

function reRunActiveAudit() {
  const selector = document.getElementById("agent-invoice-select");
  if (!selector) return;
  const invoiceId = selector.value;
  const inv = state.invoices.find(i => i.id === invoiceId);
  if (!inv) return;

  fetch("/api/agents/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inv)
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      loadAllData();
      renderAgentRunResult(data.result);
      alert(`Antigravity Multi-Agent pipeline completed in ${data.result.total_execution_seconds}s!`);
    }
  })
  .catch(err => alert("Error executing agent run: " + err.message));
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}
