"""VeriFact Core Domain Models Package."""

from episteme.common.models.claim import AtomicClaim, Claim, ClaimAnalysis
from episteme.common.models.conflict import Conflict
from episteme.common.models.evidence import (
    Evidence,
    EvidenceGraph,
    EvidenceSnapshot,
    EvidenceState,
)
from episteme.common.models.provenance import ProvenanceEdge, ProvenanceGroup
from episteme.common.models.research import (
    BudgetConsumption,
    ResearchAction,
    ResearchBudget,
    ResearchState,
    ResearchTask,
)
from episteme.common.models.source import Document, Passage, Source
from episteme.common.models.verdict import Citation, VerdictDecision, VerdictRecord

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
