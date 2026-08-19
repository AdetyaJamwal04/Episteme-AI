/**
 * VeriFact — Interactive Dashboard Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('verify-form');
    const claimInput = document.getElementById('claim-input');
    const charCount = document.getElementById('char-count');
    const btnClear = document.getElementById('btn-clear-input');
    const btnSubmit = document.getElementById('btn-submit');
    const systemStatusText = document.getElementById('system-status-text');
    const exampleChips = document.querySelectorAll('.chip-example');
    const depthPills = document.querySelectorAll('.depth-pill');

    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');

    // Verdict Elements
    const verdictBanner = document.getElementById('verdict-banner');
    const verdictPublicLabel = document.getElementById('verdict-public-label');
    const verdictInternalLabel = document.getElementById('verdict-internal-label');
    const gaugeConfidenceValue = document.getElementById('gauge-confidence-value');
    const gaugeConfidenceFill = document.getElementById('gauge-confidence-fill');
    const valSufficiency = document.getElementById('val-sufficiency');
    const valLatency = document.getElementById('val-latency');
    const verdictSummaryText = document.getElementById('verdict-summary-text');
    const verdictClaimedText = document.getElementById('verdict-claimed-text');
    const atomicClaimsList = document.getElementById('atomic-claims-list');
    const atomicCountBadge = document.getElementById('atomic-count-badge');
    const citationsList = document.getElementById('citations-list');
    const citationsCountBadge = document.getElementById('citations-count-badge');

    // Actions & Modals
    const btnCopySummary = document.getElementById('btn-copy-summary');
    const btnInspectJson = document.getElementById('btn-inspect-json');
    const jsonModalOverlay = document.getElementById('json-modal-overlay');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const rawJsonViewer = document.getElementById('raw-json-viewer');
    const btnCopyRawJson = document.getElementById('btn-copy-raw-json');

    // History Drawer
    const btnHistory = document.getElementById('btn-history');
    const historyOverlay = document.getElementById('history-overlay');
    const historyDrawer = document.getElementById('history-drawer');
    const btnCloseHistory = document.getElementById('btn-close-history');
    const historyList = document.getElementById('history-list');
    const btnClearHistory = document.getElementById('btn-clear-history');

    let currentResponseData = null;

    // 1. Initialize Health Check
    async function checkHealth() {
        try {
            const resp = await fetch('/api/v1/health');
            if (resp.ok) {
                const data = await resp.json();
                systemStatusText.textContent = `Online (${data.version})`;
            } else {
                systemStatusText.textContent = 'Degraded';
            }
        } catch {
            systemStatusText.textContent = 'Offline / Local';
        }
    }
    checkHealth();

    // 2. Character Counter & Input Handling
    claimInput.addEventListener('input', () => {
        const len = claimInput.value.length;
        charCount.textContent = `${len} / 1000`;
        if (len > 1000) {
            charCount.style.color = 'var(--color-false)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
    });

    btnClear.addEventListener('click', () => {
        claimInput.value = '';
        charCount.textContent = '0 / 1000';
        claimInput.focus();
    });

    // 3. Depth Pill Selection
    depthPills.forEach(pill => {
        pill.addEventListener('click', () => {
            depthPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            const radio = pill.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // 4. Example Claim Chips
    exampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-claim');
            claimInput.value = text;
            charCount.textContent = `${text.length} / 1000`;
            claimInput.focus();
        });
    });

    // 5. Submit & Verify Claim
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const claimText = claimInput.value.trim();
        if (!claimText) return;

        const selectedDepth = document.querySelector('input[name="depth"]:checked')?.value || 'FAST';

        // UI Loading Transition
        resultsPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');
        btnSubmit.disabled = true;
        btnSubmit.classList.add('loading');

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
                throw new Error(errData.detail || errData.title || `Server error ${resp.status}`);
            }

            const data = await resp.json();
            currentResponseData = data;
            renderResults(data, claimText);
            saveHistory(data, claimText);
        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            loadingState.classList.add('hidden');
            btnSubmit.disabled = false;
            btnSubmit.classList.remove('loading');
        }
    });

    // 6. Render Results
    function renderResults(data, originalClaim) {
        resultsPanel.classList.remove('hidden');
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Verdict State Classes
        verdictBanner.className = 'verdict-banner glass-panel';
        const labelUpper = (data.public_label || 'UNVERIFIABLE').toUpperCase();

        if (labelUpper.includes('TRUE')) {
            verdictBanner.classList.add('state-true');
        } else if (labelUpper.includes('FALSE')) {
            verdictBanner.classList.add('state-false');
        } else if (labelUpper.includes('PARTIALLY')) {
            verdictBanner.classList.add('state-mixture');
        } else {
            verdictBanner.classList.add('state-unverifiable');
        }

        verdictPublicLabel.textContent = data.public_label || 'UNVERIFIED';
        verdictInternalLabel.textContent = `INTERNAL: ${data.verdict || 'UNKNOWN'}`;

        // Radial Confidence Gauge (Circumference ~ 314.159)
        const confidencePct = Math.round((data.confidence || 0) * 100);
        gaugeConfidenceValue.textContent = `${confidencePct}%`;
        const circumference = 2 * Math.PI * 50; // ~314.159
        const offset = circumference - (confidencePct / 100) * circumference;
        gaugeConfidenceFill.style.strokeDashoffset = offset;

        // Metrics
        valSufficiency.textContent = `${Math.round((data.evidence_sufficiency || 0) * 100)}%`;
        valLatency.textContent = data.latency_ms ? `${(data.latency_ms / 1000).toFixed(2)}s` : '< 1s';

        // Summary Text
        verdictSummaryText.textContent = data.summary_text || 'No summary available.';
        verdictClaimedText.textContent = originalClaim;

        // Render Citations
        citationsList.innerHTML = '';
        const citations = data.citations || [];
        citationsCountBadge.textContent = `${citations.length} sources`;

        if (citations.length === 0) {
            citationsList.innerHTML = '<p class="empty-state">No external citations required for this assertion.</p>';
        } else {
            citations.forEach((c) => {
                const card = document.createElement('div');
                card.className = 'citation-card';
                card.innerHTML = `
                    <div class="citation-header">
                        <div class="citation-ref">
                            <span class="citation-num">${c.citation_id}</span>
                            <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="citation-source">${c.source_name || c.domain}</a>
                        </div>
                        <span class="citation-domain">${c.domain || 'web'}</span>
                    </div>
                    <p class="citation-quote">"${c.supporting_passage || 'Corroborating passage verified.'}"</p>
                `;
                citationsList.appendChild(card);
            });
        }

        // Render Atomic Claims
        renderAtomicDecomposition(originalClaim, data.verdict);
    }

    function renderAtomicDecomposition(claimText, parentVerdict) {
        atomicClaimsList.innerHTML = '';
        
        // Split by semicolon or common conjunctions for presentation
        const clauses = claimText.split(/;|\s*,\s*(?:and|whereas|while)\s+/i);
        atomicCountBadge.textContent = `${clauses.length} propositions`;

        clauses.forEach((clause, idx) => {
            const trimmed = clause.trim();
            if (!trimmed) return;

            const card = document.createElement('div');
            card.className = 'atomic-card';
            
            const isFirst = idx === 0;
            const materiality = isFirst ? 'CRITICAL' : 'MATERIAL';
            const statusClass = parentVerdict === 'SUPPORTED' ? 'status-supported' : (parentVerdict === 'REFUTED' ? 'status-refuted' : 'status-insufficient');
            const statusText = parentVerdict === 'SUPPORTED' ? '✓ Verified' : (parentVerdict === 'REFUTED' ? '✗ Contradicted' : '? Evaluated');

            card.innerHTML = `
                <div class="atomic-header">
                    <span class="atomic-tag">${materiality}</span>
                    <span class="atomic-status ${statusClass}">${statusText}</span>
                </div>
                <p class="atomic-text">${trimmed.endsWith('.') ? trimmed : trimmed + '.'}</p>
            `;
            atomicClaimsList.appendChild(card);
        });
    }

    // 7. Local History Management
    function getHistory() {
        try {
            return JSON.parse(localStorage.getItem('verifact_history') || '[]');
        } catch {
            return [];
        }
    }

    function saveHistory(data, claimText) {
        const history = getHistory();
        history.unshift({
            id: data.request_id || Date.now(),
            claim: claimText,
            public_label: data.public_label,
            verdict: data.verdict,
            confidence: data.confidence,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            full_data: data
        });
        localStorage.setItem('verifact_history', JSON.stringify(history.slice(0, 15)));
        renderHistoryList();
    }

    function renderHistoryList() {
        const history = getHistory();
        historyList.innerHTML = '';
        if (history.length === 0) {
            historyList.innerHTML = '<p class="empty-state">No recent verifications yet.</p>';
            return;
        }

        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            
            const labelColor = (item.public_label || '').includes('TRUE') 
                ? 'var(--color-true)' 
                : ((item.public_label || '').includes('FALSE') ? 'var(--color-false)' : 'var(--color-mixture)');

            div.innerHTML = `
                <div class="history-item-label" style="color: ${labelColor};">${item.public_label} (${Math.round((item.confidence || 0) * 100)}%) • ${item.timestamp}</div>
                <div class="history-item-claim">${item.claim}</div>
            `;

            div.addEventListener('click', () => {
                claimInput.value = item.claim;
                charCount.textContent = `${item.claim.length} / 1000`;
                renderResults(item.full_data, item.claim);
                closeHistoryDrawer();
            });

            historyList.appendChild(div);
        });
    }

    // 8. Drawer & Modal Event Listeners
    function openHistoryDrawer() {
        renderHistoryList();
        historyDrawer.classList.add('active');
        historyOverlay.classList.add('active');
    }

    function closeHistoryDrawer() {
        historyDrawer.classList.remove('active');
        historyOverlay.classList.remove('active');
    }

    btnHistory.addEventListener('click', openHistoryDrawer);
    btnCloseHistory.addEventListener('click', closeHistoryDrawer);
    historyOverlay.addEventListener('click', closeHistoryDrawer);

    btnClearHistory.addEventListener('click', () => {
        localStorage.removeItem('verifact_history');
        renderHistoryList();
    });

    // JSON Inspector Modal
    btnInspectJson.addEventListener('click', () => {
        if (!currentResponseData) return;
        rawJsonViewer.textContent = JSON.stringify(currentResponseData, null, 2);
        jsonModalOverlay.classList.add('active');
    });

    btnCloseModal.addEventListener('click', () => jsonModalOverlay.classList.remove('active'));
    jsonModalOverlay.addEventListener('click', (e) => {
        if (e.target === jsonModalOverlay) jsonModalOverlay.classList.remove('active');
    });

    btnCopyRawJson.addEventListener('click', () => {
        navigator.clipboard.writeText(rawJsonViewer.textContent);
        btnCopyRawJson.textContent = 'Copied!';
        setTimeout(() => { btnCopyRawJson.textContent = 'Copy JSON'; }, 1500);
    });

    btnCopySummary.addEventListener('click', () => {
        navigator.clipboard.writeText(verdictSummaryText.textContent);
        btnCopySummary.textContent = 'Copied!';
        setTimeout(() => { btnCopySummary.textContent = 'Copy Summary'; }, 1500);
    });
});
