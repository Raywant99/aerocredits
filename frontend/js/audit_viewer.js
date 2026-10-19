/**
 * AeroCredits Immutable Regulatory Audit Ledger & Cryptographic Verifier.
 * Proves tamper-evident hash chaining across all financial and agent transactions.
 */

async function renderAuditTrail() {
  const tbody = document.getElementById("audit-blocks-tbody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/audit/chain?limit=100");
    const data = await res.json();

    if (!data.success) {
      tbody.innerHTML = `<tr><td colspan="7" style="color:var(--accent-red);">Failed to load audit chain.</td></tr>`;
      return;
    }

    const blocks = data.chain.reverse(); // Show latest blocks first
    tbody.innerHTML = blocks.map(block => {
      const isGenesis = block.block_height === 0;
      const isHitl = block.action.includes("HITL");
      const isAuto = block.action.includes("GOVERNANCE");

      let actionBadge = `<span class="badge" style="background:var(--bg-elevated); color:var(--text-secondary);">${block.action}</span>`;
      if (isHitl) {
        actionBadge = `<span class="badge badge-hitl">👤 ${block.action}</span>`;
      } else if (isAuto) {
        actionBadge = `<span class="badge badge-auto-approved">🤖 ${block.action}</span>`;
      }

      return `
        <tr>
          <td><strong style="color:var(--accent-cyan);">#${block.block_height}</strong></td>
          <td style="font-size:0.75rem; color:var(--text-muted);">${block.timestamp.replace("T", " ").substring(0, 19)}</td>
          <td><span style="font-weight:600; font-size:0.78rem; color:${block.actor_agent.startsWith('HUMAN') ? 'var(--accent-amber)' : 'var(--text-primary)'};">${block.actor_agent}</span></td>
          <td>${actionBadge}</td>
          <td><code style="font-size:0.75rem;">${block.entity_id}</code></td>
          <td><span class="hash-pill" title="${block.previous_hash}">${block.previous_hash.substring(0, 10)}...</span></td>
          <td><span class="hash-pill" title="${block.block_hash}">${block.block_hash.substring(0, 10)}...</span></td>
          <td>
            <button class="btn btn-outline btn-sm" onclick='showBlockDetailsModal(${JSON.stringify(block)})'>
              Inspect Block
            </button>
          </td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    console.error("Error fetching audit trail:", err);
  }
}

async function verifyAuditIntegrity() {
  const banner = document.getElementById("verification-status-banner");
  if (!banner) return;

  banner.innerHTML = `<div style="color:var(--accent-cyan);">⏳ Running SHA-256 cryptographic verification across all blocks in the ledger...</div>`;

  try {
    const res = await fetch("/api/audit/verify");
    const data = await res.json();

    if (data.success && data.verification.is_valid) {
      banner.innerHTML = `
        <div class="verification-content">
          <div class="verification-icon">🛡️</div>
          <div>
            <div style="font-weight:700; color:var(--accent-green); font-size:1.05rem;">
              Cryptographic Integrity Verified: Zero Tampering Detected
            </div>
            <div style="font-size:0.78rem; color:var(--text-secondary);">
              All ${data.verification.total_blocks} chained blocks verified against SHA-256 hash proofs (Block Height #0 to #${data.verification.latest_block_height}). Compliant with Basel III & SOC2 audit standards.
            </div>
          </div>
        </div>
        <button class="btn btn-outline btn-sm" onclick="verifyAuditIntegrity()">
          🔄 Re-Verify Ledger
        </button>
      `;
    } else {
      banner.innerHTML = `
        <div class="verification-content">
          <div class="verification-icon" style="color:var(--accent-red);">⚠️</div>
          <div>
            <div style="font-weight:700; color:var(--accent-red); font-size:1.05rem;">
              Tampering Detected in Ledger!
            </div>
            <div style="font-size:0.78rem; color:var(--text-secondary);">
              ${data.verification.reason || "Hash pointer mismatch"}
            </div>
          </div>
        </div>
      `;
    }
  } catch (err) {
    alert("Verification failed: " + err.message);
  }
}

async function exportRegulatoryPackage() {
  try {
    const res = await fetch("/api/audit/export");
    const data = await res.json();

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const dlAnchorElem = document.createElement("a");
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `AeroCredits_Regulatory_Audit_Report_${new Date().toISOString().split('T')[0]}.json`);
    dlAnchorElem.click();
  } catch (err) {
    alert("Error exporting regulatory package: " + err.message);
  }
}

function showBlockDetailsModal(block) {
  const modal = document.getElementById("modal-block-details");
  if (!modal) return;

  document.getElementById("block-detail-height").textContent = `#${block.block_height}`;
  document.getElementById("block-detail-actor").textContent = block.actor_agent;
  document.getElementById("block-detail-action").textContent = block.action;
  document.getElementById("block-detail-entity").textContent = block.entity_id;
  document.getElementById("block-detail-timestamp").textContent = block.timestamp;
  document.getElementById("block-detail-prevhash").textContent = block.previous_hash;
  document.getElementById("block-detail-currhash").textContent = block.block_hash;
  document.getElementById("block-detail-payload").textContent = JSON.stringify(block.data_payload, null, 2);

  modal.classList.add("active");
}

function closeBlockModal() {
  const modal = document.getElementById("modal-block-details");
  if (modal) modal.classList.remove("active");
}
