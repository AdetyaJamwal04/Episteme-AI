"""Sub-Goal Formulator and Search Query Optimizer.

Generates targeted search queries for unresolved atomic propositions and constructs
specialized conflict-resolution queries targeting primary institutional archives.
"""

from uuid import UUID

from episteme.claims.entity_extractor import extract_named_entities
from episteme.claims.temporal_extractor import extract_temporal_constraints
from episteme.common.models.claim import AtomicClaim
from episteme.common.models.conflict import Conflict


class QueryFormulator:
    """Formulates and optimizes search queries across research iterations."""

    def formulate_initial_queries(
        self,
        atomic_claims: list[AtomicClaim],
        max_queries: int = 5,
    ) -> list[tuple[UUID, str]]:
        """Generate first-pass search queries for decomposed atomic propositions.

        Args:
            atomic_claims: List of atomic propositions.
            max_queries: Maximum queries to return.

        Returns:
            list[tuple[UUID, str]]: List of (atomic_claim_id, query_string).
        """
        queries: list[tuple[UUID, str]] = []
        for ac in atomic_claims[:max_queries]:
            # Use proposition text directly for initial pass
            queries.append((ac.atomic_claim_id, ac.text.strip()))
        return queries

    def formulate_refinement_queries(
        self,
        unresolved_atomic_claims: list[AtomicClaim],
        past_queries: list[str],
        max_queries: int = 3,
    ) -> list[tuple[UUID, str]]:
        """Generate targeted sub-queries for unverified or low-coverage atomic claims.

        Args:
            unresolved_atomic_claims: Atomic propositions needing additional evidence.
            past_queries: Set/list of previously executed queries to avoid redundancy.
            max_queries: Maximum new queries to generate.

        Returns:
            list[tuple[UUID, str]]: List of (atomic_claim_id, refined_query).
        """
        refined_queries: list[tuple[UUID, str]] = []
        seen = {q.lower() for q in past_queries}

        for ac in unresolved_atomic_claims:
            if len(refined_queries) >= max_queries:
                break

            entities = extract_named_entities(ac.text)
            temporals = extract_temporal_constraints(ac.text)

            entity_str = " ".join(e["text"] for e in entities[:3])
            temp_str = " ".join(str(t.get("year", "")) for t in temporals if "year" in t)

            # Construct targeted keyword query with domain qualifiers
            candidate_query = f"{entity_str} {temp_str} official documentation report".strip()
            if not candidate_query or candidate_query.lower() in seen:
                candidate_query = f"{ac.text} primary sources official records"

            if candidate_query.lower() not in seen:
                refined_queries.append((ac.atomic_claim_id, candidate_query))
                seen.add(candidate_query.lower())

        return refined_queries

    def formulate_conflict_resolution_queries(
        self,
        conflicts: list[Conflict],
        atomic_claims_by_id: dict[UUID, AtomicClaim],
        past_queries: list[str],
        max_queries: int = 2,
    ) -> list[tuple[UUID, str]]:
        """Generate authoritative primary-source queries specifically targeting detected contradictions.

        Args:
            conflicts: List of detected opposing evidence conflicts.
            atomic_claims_by_id: Map of atomic_claim_id to AtomicClaim.
            past_queries: Previously executed queries.
            max_queries: Maximum queries.

        Returns:
            list[tuple[UUID, str]]: List of (atomic_claim_id, conflict_query).
        """
        conflict_queries: list[tuple[UUID, str]] = []
        seen = {q.lower() for q in past_queries}

        for conf in conflicts:
            if len(conflict_queries) >= max_queries:
                break

            ac = atomic_claims_by_id.get(conf.atomic_claim_id)
            if not ac:
                continue

            query = f"{ac.text} official archives government statement factual record"
            if query.lower() not in seen:
                conflict_queries.append((ac.atomic_claim_id, query))
                seen.add(query.lower())

        return conflict_queries
