# Episteme Evaluation Report — Seed Benchmark v1 (50 Claims)

## 1. Executive Summary & Quality Gates

| Metric | Value | Production Target | Status |
| :--- | :--- | :--- | :--- |
| **Macro-F1** | `75.8%` | $\ge 80.0\%$ | ⚠️ IN REVIEW |
| **Overall Accuracy** | `84.0%` | $\ge 85.0\%$ | ⚠️ IN REVIEW |
| **Expected Calibration Error (ECE)** | `0.1908` | $\le 0.0800$ | ⚠️ IN REVIEW |
| **Brier Score** | `0.1538` | $\le 0.1500$ | ⚠️ IN REVIEW |
| **Total Claims Evaluated** | `50` | `50` | ✅ COMPLETE |

---

## 2. Per-Verdict Epistemic Class Performance

| Canonical Verdict Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| `SUPPORTED` | 87.5% | 100.0% | **93.3%** | 14 |
| `REFUTED` | 89.5% | 100.0% | **94.4%** | 17 |
| `PARTIALLY_SUPPORTED` | 100.0% | 11.1% | **20.0%** | 9 |
| `INSUFFICIENT_EVIDENCE` | 55.6% | 100.0% | **71.4%** | 5 |
| `UNVERIFIABLE` | 100.0% | 100.0% | **100.0%** | 5 |

---

## 3. Confusion Matrix

| True \ Predicted | `SUPPORTED` | `REFUTED` | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | `UNVERIFIABLE` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `SUPPORTED` | 14 | 0 | 0 | 0 | 0 |
| `REFUTED` | 0 | 17 | 0 | 0 | 0 |
| `PARTIALLY_SUPPORTED` | 2 | 2 | 1 | 4 | 0 |
| `INSUFFICIENT_EVIDENCE` | 0 | 0 | 0 | 5 | 0 |
| `UNVERIFIABLE` | 0 | 0 | 0 | 0 | 5 |

---

## 4. Performance by Claim Category

| Category | Total | Correct | Accuracy | Avg Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **AEROSPACE** | 1 | 1 | 100.0% | 71.9% |
| **AESTHETICS** | 1 | 1 | 100.0% | 100.0% |
| **ANCIENT_HISTORY** | 1 | 1 | 100.0% | 40.0% |
| **ASTRONOMY** | 1 | 1 | 100.0% | 71.3% |
| **ASTROPHYSICS** | 1 | 1 | 100.0% | 71.7% |
| **BIOTECHNOLOGY** | 1 | 1 | 100.0% | 72.0% |
| **BUSINESS** | 5 | 3 | 60.0% | 65.5% |
| **CLIMATE** | 1 | 1 | 100.0% | 71.7% |
| **COMPUTING** | 1 | 1 | 100.0% | 71.6% |
| **CRYPTOGRAPHY** | 1 | 1 | 100.0% | 40.0% |
| **DEMOGRAPHICS** | 1 | 1 | 100.0% | 72.0% |
| **ECONOMICS** | 2 | 1 | 50.0% | 71.9% |
| **ETHICS** | 1 | 1 | 100.0% | 100.0% |
| **EVENTS** | 1 | 1 | 100.0% | 71.2% |
| **FINANCE** | 3 | 3 | 100.0% | 71.5% |
| **GENETICS** | 1 | 1 | 100.0% | 80.0% |
| **GEOGRAPHY** | 2 | 1 | 50.0% | 67.4% |
| **GEOPOLITICS** | 2 | 2 | 100.0% | 60.0% |
| **HARDWARE** | 1 | 0 | 0.0% | 60.0% |
| **HISTORY** | 7 | 6 | 85.7% | 66.3% |
| **MEDICINE** | 3 | 3 | 100.0% | 71.9% |
| **NEUROSCIENCE** | 1 | 1 | 100.0% | 71.6% |
| **PHILOSOPHY** | 1 | 1 | 100.0% | 100.0% |
| **PHYSICS** | 1 | 1 | 100.0% | 72.0% |
| **POLICY** | 1 | 1 | 100.0% | 100.0% |
| **POLITICS** | 3 | 3 | 100.0% | 71.6% |
| **SUBJECTIVE** | 1 | 1 | 100.0% | 100.0% |
| **TECH** | 3 | 1 | 33.3% | 56.6% |
| **VENTURE_CAPITAL** | 1 | 1 | 100.0% | 40.0% |

---

## 5. Error Analysis & Discrepancies (8 Discrepancies)

| Claim ID | Claim Text | Expected | Predicted | Confidence | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `VF-BM-022` | Tesla delivered 2.5 million vehicles globally... | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | 71.6% | SUFFICIENT_EVIDENCE |
| `VF-BM-023` | The US national unemployment rate fell to 1.5... | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | 71.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-024` | OpenAI was founded in December 2015 as a for-... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 61.2% | EVALUATION_COMPLETE |
| `VF-BM-025` | NASA's Apollo 11 mission landed Neil Armstron... | `PARTIALLY_SUPPORTED` | `REFUTED` | 58.3% | EVALUATION_COMPLETE |
| `VF-BM-030` | Twitter operates under the corporate name Twi... | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | 72.0% | SUFFICIENT_EVIDENCE |
| `VF-BM-036` | Google was founded by Larry Page and Sergey B... | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | 43.6% | EVALUATION_COMPLETE |
| `VF-BM-037` | The Panama Canal connects the Atlantic and Pa... | `PARTIALLY_SUPPORTED` | `REFUTED` | 63.1% | EVALUATION_COMPLETE |
| `VF-BM-040` | Nvidia designed the H100 GPU architecture, wh... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 60.0% | EVALUATION_COMPLETE |
