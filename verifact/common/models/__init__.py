"""VeriFact Core Domain Models Package."""

from verifact.common.models.claim import AtomicClaim, Claim, ClaimAnalysis
from verifact.common.models.conflict import Conflict
from verifact.common.models.evidence import (
    Evidence,
    EvidenceGraph,
    EvidenceSnapshot,
    EvidenceState,
)
from verifact.common.models.provenance import ProvenanceEdge, ProvenanceGroup
from verifact.common.models.research import (
    BudgetConsumption,
    ResearchAction,
    ResearchBudget,
    ResearchState,
    ResearchTask,
)
from verifact.common.models.source import Document, Passage, Source
from verifact.common.models.verdict import Citation, VerdictDecision, VerdictRecord

__all__ = [
    "AtomicClaim",
    "BudgetConsumption",
    "Citation",
    "Claim",
    "ClaimAnalysis",
    "Conflict",
    "Document",
    "Evidence",
    "EvidenceGraph",
    "EvidenceSnapshot",
    "EvidenceState",
    "Passage",
    "ProvenanceEdge",
    "ProvenanceGroup",
    "ResearchAction",
    "ResearchBudget",
    "ResearchState",
    "ResearchTask",
    "Source",
    "VerdictDecision",
    "VerdictRecord",
]
