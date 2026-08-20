/**
 * Episteme — Discover What the Evidence Supports
 * Application Logic & Epistemic Workbench Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Rail View Switching
    const railItems = document.querySelectorAll('.rail-item[data-view]');
    const viewContainers = document.querySelectorAll('.view-container');
    const currentViewTitle = document.getElementById('current-view-title');

    railItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetViewId = item.getAttribute('data-view');
            railItems.forEach(r => r.classList.remove('active'));
            item.classList.add('active');

            viewContainers.forEach(vc => {
                if (vc.id === targetViewId) {
                    vc.classList.add('active');
                } else {
                    vc.classList.remove('active');
                }
            });

            if (targetViewId === 'verifier-view') {
                currentViewTitle.textContent = 'Discover What the Evidence Supports';
            } else if (targetViewId === 'benchmarks-view') {
                currentViewTitle.textContent = 'Episteme Calibration & Benchmark Telemetry';
            } else if (targetViewId === 'history-view') {
                currentViewTitle.textContent = 'Investigation Audit Log';
                renderAuditHistory();
            }
        });
    });

    // 2. Workbench Tab Switching
    const wbTabs = document.querySelectorAll('.wb-tab');
    const tabContents = document.querySelectorAll('.tab-content');

    wbTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTabId = tab.getAttribute('data-tab');
            wbTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            tabContents.forEach(tc => {
                if (tc.id === targetTabId) {
                    tc.classList.add('active');
                } else {
                    tc.classList.remove('active');
                }
            });
        });
    });

    // 3. Elements & Form Controls
    const form = document.getElementById('verify-form');
    const claimInput = document.getElementById('claim-input');
    const charCount = document.getElementById('char-count');
    const btnClearInput = document.getElementById('btn-clear-input');
    const btnSubmit = document.getElementById('btn-submit');
    const systemStatusPill = document.getElementById('system-status-pill');
    const segPills = document.querySelectorAll('.seg-pill');
    const scenarioChips = document.querySelectorAll('.scenario-chip');

    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');

    // Verdict Elements
    const verdictBanner = document.getElementById('verdict-banner');
    const verdictPublicLabel = document.getElementById('verdict-public-label');
    const verdictInternalLabel = document.getElementById('verdict-internal-label');
    const valSufficiency = document.getElementById('val-sufficiency');
    const valLatency = document.getElementById('val-latency');
    const valStopReason = document.getElementById('val-stop-reason');
    const dialConfidenceNum = document.getElementById('dial-confidence-num');
    const dialConfidenceBar = document.getElementById('dial-confidence-bar');
    const verdictSummaryText = document.getElementById('verdict-summary-text');
    const verdictClaimedText = document.getElementById('verdict-claimed-text');

    const atomicClaimsList = document.getElementById('atomic-claims-list');
    const atomicCountBadge = document.getElementById('atomic-count-badge');
    const citationsList = document.getElementById('citations-list');
    const tabEvidenceCount = document.getElementById('tab-evidence-count');
    const evidenceFilterSelect = document.getElementById('evidence-filter-select');

    // Export Tab Elements
    const markdownReportPreview = document.getElementById('markdown-report-preview');
    const curlSnippetPreview = document.getElementById('curl-snippet-preview');
    const btnCopyMarkdown = document.getElementById('btn-copy-markdown-report');
    const btnDownloadJson = document.getElementById('btn-download-report-json');
    const btnCopyCurl = document.getElementById('btn-copy-curl');

    // Settings Modal
    const btnOpenSettings = document.getElementById('btn-open-settings');
    const btnCloseSettings = document.getElementById('btn-close-settings');
    const settingsModal = document.getElementById('settings-modal');
    const btnSaveSettings = document.getElementById('btn-save-settings');

    // Audit Log
    const auditHistoryContainer = document.getElementById('audit-history-container');
    const btnPurgeHistory = document.getElementById('btn-purge-history');

    let currentVerificationData = null;

    // 4. System Health Polling
    async function pollHealth() {
        try {
            const resp = await fetch('/api/v1/health');
            if (resp.ok) {
                const data = await resp.json();
                systemStatusPill.textContent = `Epistemic Engine Online (v${data.version})`;
            }
        } catch {
            systemStatusPill.textContent = 'Episteme Local Standalone';
        }
    }
    pollHealth();

    // 5. Input Character Counter & Tools
    claimInput.addEventListener('input', () => {
        const len = claimInput.value.length;
        charCount.textContent = `${len} / 1000`;
        if (len > 1000) {
            charCount.style.color = 'var(--color-refuted)';
        } else {
            charCount.style.color = 'var(--text-dim)';
        }
    });

    btnClearInput.addEventListener('click', () => {
        claimInput.value = '';
        charCount.textContent = '0 / 1000';
        claimInput.focus();
    });

    // 6. Research Depth Pill Selector
    segPills.forEach(pill => {
        pill.addEventListener('click', () => {
            segPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            const radio = pill.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // 7. Scenario Chips
    scenarioChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-claim');
            claimInput.value = text;
            charCount.textContent = `${text.length} / 1000`;
            claimInput.focus();
        });
    });

    // 8. Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
        if (e.key === 'Escape') {
            settingsModal.classList.remove('active');
        }
    });

    // 9. Submit & Execute Verification
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const claimText = claimInput.value.trim();
        if (!claimText) return;

        const selectedDepth = document.querySelector('input[name="depth"]:checked')?.value || 'STANDARD';

        // Transition UI to processing state
        resultsPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');
        btnSubmit.disabled = true;

        try {
            const resp = await fetch('/api/v1/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    claim: claimText,
                    depth: selectedDepth
                })
            });

            if (!resp.ok) {
                const errData = await resp.json().catch(() => ({ detail: 'Verification failed' }));
                throw new Error(errData.detail || errData.title || `Server error (${resp.status})`);
            }

            const data = await resp.json();
            currentVerificationData = data;
            renderAllResults(data, claimText, selectedDepth);
            saveToAuditLog(data, claimText);
            showToast('Epistemic examination complete!');
        } catch (err) {
            showToast(`Error: ${err.message}`, 'error');
        } finally {
            loadingState.classList.add('hidden');
            btnSubmit.disabled = false;
        }
    });

    // 10. Render Complete Results
    function renderAllResults(data, originalClaim, selectedDepth) {
        resultsPanel.classList.remove('hidden');

        // State classes
        verdictBanner.className = 'verdict-hero-card';
        const labelUpper = (data.public_label || 'UNVERIFIABLE').toUpperCase();

        if (labelUpper.includes('TRUE')) {
            verdictBanner.classList.add('state-true');
        } else if (labelUpper.includes('FALSE')) {
            verdictBanner.classList.add('state-false');
        } else if (labelUpper.includes('PARTIALLY')) {
            verdictBanner.classList.add('state-mixture');
        }

        verdictPublicLabel.textContent = data.public_label || 'UNVERIFIED';
        verdictInternalLabel.textContent = `INTERNAL: ${data.verdict || 'UNKNOWN'}`;

        // Top Metadata
        valSufficiency.textContent = `${Math.round((data.evidence_sufficiency || 0) * 100)}%`;
        valLatency.textContent = data.latency_ms ? `${(data.latency_ms / 1000).toFixed(2)}s` : '< 1s';
        valStopReason.textContent = data.stop_reason || 'COMPLETE';

        // Confidence Dial (circumference ~ 364.42)
        const confidencePct = Math.round((data.confidence || 0) * 100);
        dialConfidenceNum.textContent = `${confidencePct}%`;
        const circumference = 2 * Math.PI * 58; // 364.42
        const offset = circumference - (confidencePct / 100) * circumference;
        dialConfidenceBar.style.strokeDashoffset = offset;

        // Synthesis and Claim Texts
        verdictSummaryText.textContent = data.summary_text || 'Synthesis complete.';
        verdictClaimedText.textContent = originalClaim;

        // Render Atomic Propositions
        renderAtomicPropositions(originalClaim, data.verdict);

        // Render Evidence Sources
        renderEvidenceMatrix(data.citations || []);

        // Render Export Tab
        renderExportTab(data, originalClaim, selectedDepth);
    }

    function renderAtomicPropositions(claimText, parentVerdict) {
        atomicClaimsList.innerHTML = '';
        const clauses = claimText.split(/;|\s*,\s*(?:and|whereas|while)\s+/i);
        atomicCountBadge.textContent = `${clauses.length} proposition${clauses.length > 1 ? 's' : ''}`;

        clauses.forEach((clause) => {
            const trimmed = clause.trim();
            if (!trimmed) return;

            const row = document.createElement('div');
            row.className = 'atomic-proposition-row';
            
            const isRefuted = parentVerdict === 'REFUTED';
            const tagClass = isRefuted ? 'contradicted' : (parentVerdict === 'SUPPORTED' ? 'verified' : 'uncertain');
            const tagText = isRefuted ? 'Contradicted' : (parentVerdict === 'SUPPORTED' ? 'Verified' : 'Evaluated');

            row.innerHTML = `
                <span class="prop-text">${trimmed.endsWith('.') ? trimmed : trimmed + '.'}</span>
                <span class="prop-status-tag ${tagClass}">${tagText}</span>
            `;
            atomicClaimsList.appendChild(row);
        });
    }

    function renderEvidenceMatrix(citations) {
        citationsList.innerHTML = '';
        tabEvidenceCount.textContent = citations.length;

        if (citations.length === 0) {
            citationsList.innerHTML = '<p class="empty-state">No external citations returned for this statement.</p>';
            return;
        }

        citations.forEach(c => {
            const card = document.createElement('div');
            card.className = 'evidence-source-card';
            card.setAttribute('data-authority', c.authority_class || 'SECONDARY');

            card.innerHTML = `
                <div class="source-card-header">
                    <div class="source-link-group">
                        <span class="source-index-num">${c.citation_id}</span>
                        <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="source-title-link">
                            ${c.source_name || c.domain}
                        </a>
                    </div>
                    <span class="source-domain-pill">${c.domain || 'web'}</span>
                </div>
                <div class="source-quote-block">
                    "${c.supporting_passage || 'Passage verified by stance classifier.'}"
                </div>
            `;
            citationsList.appendChild(card);
        });
    }

    // Evidence Filter Select
    evidenceFilterSelect.addEventListener('change', () => {
        const filterVal = evidenceFilterSelect.value;
        const cards = citationsList.querySelectorAll('.evidence-source-card');
        cards.forEach(card => {
            if (filterVal === 'ALL') {
                card.style.display = 'block';
            } else {
                const auth = card.getAttribute('data-authority');
                card.style.display = (auth === filterVal) ? 'block' : 'none';
            }
        });
    });

    // 11. Export Tab Generator
    function renderExportTab(data, originalClaim, depth) {
        // Markdown Report
        const mdReport = `# Episteme Investigation Dossier
*Discover What the Evidence Supports*

**Date:** ${new Date().toUTCString()}
**Request ID:** \`${data.request_id}\`

## 1. Verified Proposition
> "${originalClaim}"

## 2. Epistemic Verdict
- **Public Label:** **${data.public_label}**
- **Internal Verdict:** \`${data.verdict}\`
- **Calibrated Confidence:** **${Math.round((data.confidence || 0) * 100)}%**
- **Evidence Sufficiency:** ${Math.round((data.evidence_sufficiency || 0) * 100)}%
- **Engine Latency:** ${data.latency_ms ? (data.latency_ms / 1000).toFixed(2) + 's' : 'N/A'}

## 3. Grounded Epistemic Synthesis
${data.summary_text}

## 4. Primary Citations
${(data.citations || []).map(c => `- **[${c.citation_id}] ${c.source_name}** (${c.domain})\n  *URL:* ${c.url}\n  *Quote:* "${c.supporting_passage}"`).join('\n\n')}
`;
        markdownReportPreview.value = mdReport;

        // cURL Snippet
        const curlSnippet = `curl -X POST "http://localhost:8000/api/v1/check" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({ claim: originalClaim, depth: depth }, null, 2)}'`;
        curlSnippetPreview.textContent = curlSnippet;
    }

    btnCopyMarkdown.addEventListener('click', () => {
        navigator.clipboard.writeText(markdownReportPreview.value);
        showToast('Episteme dossier copied to clipboard!');
    });

    btnCopyCurl.addEventListener('click', () => {
        navigator.clipboard.writeText(curlSnippetPreview.textContent);
        showToast('cURL command copied!');
    });

    btnDownloadJson.addEventListener('click', () => {
        if (!currentVerificationData) return;
        const blob = new Blob([JSON.stringify(currentVerificationData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `episteme_dossier_${currentVerificationData.request_id || Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Episteme JSON dossier downloaded!');
    });

    // 12. Audit History (LocalStorage)
    function getAuditLog() {
        try {
            return JSON.parse(localStorage.getItem('episteme_audit_log') || '[]');
        } catch {
            return [];
        }
    }

    function saveToAuditLog(data, claimText) {
        const log = getAuditLog();
        log.unshift({
            id: data.request_id || Date.now(),
            claim: claimText,
            public_label: data.public_label,
            verdict: data.verdict,
            confidence: data.confidence,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            full_data: data
        });
        localStorage.setItem('episteme_audit_log', JSON.stringify(log.slice(0, 30)));
    }

    function renderAuditHistory() {
        const log = getAuditLog();
        auditHistoryContainer.innerHTML = '';

        if (log.length === 0) {
            auditHistoryContainer.innerHTML = '<p class="empty-state">No past investigations found in this browser session.</p>';
            return;
        }

        log.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';
            
            const color = (item.public_label || '').includes('TRUE') 
                ? 'var(--color-verified)' 
                : ((item.public_label || '').includes('FALSE') ? 'var(--color-refuted)' : 'var(--color-mixture)');

            card.innerHTML = `
                <div class="history-top-row">
                    <span class="history-verdict-tag" style="color: ${color};">${item.public_label} (${Math.round((item.confidence || 0) * 100)}%)</span>
                    <span class="history-time">${item.time}</span>
                </div>
                <div class="history-claim-title">${item.claim}</div>
            `;

            card.addEventListener('click', () => {
                railItems[0].click();
                claimInput.value = item.claim;
                charCount.textContent = `${item.claim.length} / 1000`;
                currentVerificationData = item.full_data;
                renderAllResults(item.full_data, item.claim, 'STANDARD');
            });

            auditHistoryContainer.appendChild(card);
        });
    }

    btnPurgeHistory.addEventListener('click', () => {
        localStorage.removeItem('episteme_audit_log');
        renderAuditHistory();
        showToast('Audit history cleared');
    });

    // 13. Settings Modal
    btnOpenSettings.addEventListener('click', () => settingsModal.classList.add('active'));
    btnCloseSettings.addEventListener('click', () => settingsModal.classList.remove('active'));
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) settingsModal.classList.remove('active');
    });
    btnSaveSettings.addEventListener('click', () => {
        settingsModal.classList.remove('active');
        showToast('Episteme parameters applied');
    });

    // 14. Toast System
    function showToast(msg, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast-item ${type}`;
        toast.textContent = msg;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
});
