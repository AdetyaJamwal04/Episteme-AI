"""Provenance Clustering and Epistemic Independence Scoring.

Groups evidence and documents by canonical domain and exact quotation overlap,
assigning independence scores to prevent evidence cascade inflation.
"""

from urllib.parse import urlparse
from uuid import UUID, uuid4

from episteme.common.enums import ProvenanceDetectionMethod
from episteme.common.models.evidence import Evidence
from episteme.common.models.provenance import ProvenanceGroup
from episteme.common.models.source import Document, Passage


def _extract_domain(url: str) -> str:
    """Extract canonical domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or "unknown"
    except Exception:
        return "unknown"


def _compute_ngram_overlap(text_a: str, text_b: str, n: int = 6) -> float:
    """Compute word n-gram Jaccard similarity between two passage strings."""
    words_a = text_a.lower().split()
    words_b = text_b.lower().split()

    if len(words_a) < n or len(words_b) < n:
        return 0.0

    ngrams_a = {tuple(words_a[i : i + n]) for i in range(len(words_a) - n + 1)}
    ngrams_b = {tuple(words_b[i : i + n]) for i in range(len(words_b) - n + 1)}

    if not ngrams_a or not ngrams_b:
        return 0.0

    intersection = len(ngrams_a.intersection(ngrams_b))
    union = len(ngrams_a.union(ngrams_b))

    return intersection / max(1, union)


class ProvenanceClusterer:
    """Clusters evidence items into ProvenanceGroups and computes independence weights."""

    def cluster_evidence(
        self,
        evidence_items: list[Evidence],
        passages_by_id: dict[UUID, Passage],
        documents_by_id: dict[UUID, Document],
    ) -> tuple[list[ProvenanceGroup], list[Evidence]]:
        """Group evidence by domain and verbatim quotation overlap.

        Args:
            evidence_items: List of evaluated Evidence objects.
            passages_by_id: Mapping of passage_id to Passage object.
            documents_by_id: Mapping of document_id to Document object.

        Returns:
            tuple[list[ProvenanceGroup], list[Evidence]]: Created clusters and updated evidence with independence scores.
        """
        if not evidence_items:
            return [], []

        clusters: list[ProvenanceGroup] = []
        domain_clusters: dict[str, ProvenanceGroup] = {}
        updated_evidence: list[Evidence] = []

        # 1. First pass: Cluster by canonical URL domain
        for ev in evidence_items:
            passage = passages_by_id.get(ev.passage_id)
            doc = documents_by_id.get(passage.document_id) if passage else None
            domain = _extract_domain(doc.url) if doc else "unknown"

            if domain not in domain_clusters:
                group = ProvenanceGroup(
                    provenance_group_id=uuid4(),
                    root_source_id=doc.source_id if doc else None,
                    member_evidence_ids=[ev.evidence_id],
                    detection_method=ProvenanceDetectionMethod.URL_DOMAIN_CLUSTERING,
                    cluster_confidence=1.0,
                )
                domain_clusters[domain] = group
                clusters.append(group)
                # First document from domain gets full independence
                ev.independence_score = 1.0
                ev.provenance_group_id = group.provenance_group_id
            else:
                group = domain_clusters[domain]
                group.member_evidence_ids.append(ev.evidence_id)
                # Subsequent documents from the same domain have discounted independence
                ev.independence_score = 0.25
                ev.provenance_group_id = group.provenance_group_id

            updated_evidence.append(ev)

        # 2. Second pass: Cross-domain verbatim quotation overlap check
        for i, ev_a in enumerate(updated_evidence):
            p_a = passages_by_id.get(ev_a.passage_id)
            if not p_a:
                continue

            for j in range(i + 1, len(updated_evidence)):
                ev_b = updated_evidence[j]
                # If already in same group, skip
                if ev_a.provenance_group_id == ev_b.provenance_group_id:
                    continue

                p_b = passages_by_id.get(ev_b.passage_id)
                if not p_b:
                    continue

                overlap = _compute_ngram_overlap(p_a.text, p_b.text, n=6)
                if overlap >= 0.60:
                    # High quotation overlap: derivative syndicate copy detected
                    ev_b.independence_score = min(ev_b.independence_score, 0.20)

        return clusters, updated_evidence
