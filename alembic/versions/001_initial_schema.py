"""Initial Schema Migration with pgvector and Provenance Tables.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-08-18 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. verification_requests
    op.create_table(
        "verification_requests",
        sa.Column("request_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False, server_default="default"),
        sa.Column("raw_input", sa.String(), nullable=False),
        sa.Column("mode", sa.String(16), nullable=False, server_default="STANDARD"),
        sa.Column("status", sa.String(24), nullable=False, server_default="QUEUED"),
        sa.Column("client_metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 3. claims
    op.create_table(
        "claims",
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification_requests.request_id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_text", sa.String(), nullable=False),
        sa.Column("normalized_text", sa.String(), nullable=False),
        sa.Column("language_code", sa.String(8), nullable=False, server_default="en"),
        sa.Column("primary_type", sa.String(32), nullable=False),
        sa.Column("secondary_types", postgresql.ARRAY(sa.String()), server_default="{}"),
        sa.Column("domain", sa.String(32), nullable=False, server_default="GENERAL"),
        sa.Column("complexity", sa.String(16), nullable=False, server_default="MODERATE"),
        sa.Column("is_atomic", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("idx_claims_content_hash", "claims", ["content_hash"])

    # 4. atomic_claims
    op.create_table(
        "atomic_claims",
        sa.Column("atomic_claim_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("is_atomic", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("decomposition_depth", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("materiality", sa.String(16), nullable=False, server_default="MATERIAL"),
        sa.Column("entities", postgresql.JSONB(), server_default="{}"),
        sa.Column("temporal_scope", postgresql.JSONB(), server_default="{}"),
        sa.Column("status", sa.String(24), nullable=False, server_default="UNRESEARCHED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("idx_atomic_claims_claim_id", "atomic_claims", ["claim_id"])

    # 5. sources
    op.create_table(
        "sources",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("canonical_domain", sa.String(255), unique=True, nullable=False),
        sa.Column("publisher_name", sa.String(255), nullable=True),
        sa.Column("source_type", sa.String(32), nullable=False, server_default="UNKNOWN"),
        sa.Column("authority_class", sa.String(16), nullable=False, server_default="UNKNOWN"),
        sa.Column("domain_authority_score", sa.Float(), server_default="0.5"),
        sa.Column("country_code", sa.String(4), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # 6. documents
    op.create_table(
        "documents",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.source_id"), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("canonical_url", sa.String(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("http_status", sa.Integer(), server_default="200"),
        sa.Column("storage_uri", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("canonical_url", "content_hash", name="uq_doc_url_hash"),
    )
    op.create_index("idx_documents_canonical_url", "documents", ["canonical_url"])

    # 7. passages
    op.create_table(
        "passages",
        sa.Column("passage_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("idx_passages_doc_id", "passages", ["document_id"])

    # 8. provenance_groups
    op.create_table(
        "provenance_groups",
        sa.Column("provenance_group_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("root_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.source_id"), nullable=True),
        sa.Column("detection_method", sa.String(32), nullable=False),
        sa.Column("cluster_confidence", sa.Float(), server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # 9. evidence
    op.create_table(
        "evidence",
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("atomic_claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("atomic_claims.atomic_claim_id", ondelete="CASCADE"), nullable=False),
        sa.Column("passage_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("passages.passage_id"), nullable=False),
        sa.Column("provenance_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("provenance_groups.provenance_group_id"), nullable=True),
        sa.Column("relationship", sa.String(32), nullable=False),
        sa.Column("relevance_score", sa.Float(), server_default="0.0"),
        sa.Column("entailment_score", sa.Float(), server_default="0.0"),
        sa.Column("contradiction_score", sa.Float(), server_default="0.0"),
        sa.Column("source_quality_score", sa.Float(), server_default="0.5"),
        sa.Column("independence_score", sa.Float(), server_default="1.0"),
        sa.Column("temporal_validity_status", sa.String(24), server_default="VALID"),
        sa.Column("assessment_version", sa.String(32), server_default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("idx_evidence_atomic_claim", "evidence", ["atomic_claim_id"])
    op.create_index("idx_evidence_relationship", "evidence", ["relationship"])

    # 10. conflicts
    op.create_table(
        "conflicts",
        sa.Column("conflict_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("atomic_claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("atomic_claims.atomic_claim_id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id_a", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.evidence_id"), nullable=False),
        sa.Column("evidence_id_b", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence.evidence_id"), nullable=False),
        sa.Column("conflict_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False, server_default="MAJOR"),
        sa.Column("resolution_status", sa.String(32), nullable=False, server_default="UNRESOLVED"),
        sa.Column("resolution_rationale", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # 11. evidence_snapshots
    op.create_table(
        "evidence_snapshots",
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("provenance_group_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column("policy_version", sa.String(32), nullable=False),
        sa.Column("snapshot_checksum", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # 12. verdicts
    op.create_table(
        "verdicts",
        sa.Column("verdict_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.claim_id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_snapshots.snapshot_id"), nullable=False, unique=True),
        sa.Column("verdict", sa.String(32), nullable=False),
        sa.Column("public_label", sa.String(32), nullable=False),
        sa.Column("framing_concerns", sa.Boolean(), server_default="false"),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_sufficiency", sa.Float(), nullable=False),
        sa.Column("stop_reason", sa.String(32), nullable=False),
        sa.Column("summary_text", sa.String(), nullable=False),
        sa.Column("citations", postgresql.JSONB(), server_default="[]"),
        sa.Column("engine_version", sa.String(32), server_default="1.0.0"),
        sa.Column("calibration_version", sa.String(32), server_default="1.0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("verdicts")
    op.drop_table("evidence_snapshots")
    op.drop_table("conflicts")
    op.drop_table("evidence")
    op.drop_table("provenance_groups")
    op.drop_table("passages")
    op.drop_table("documents")
    op.drop_table("sources")
    op.drop_table("atomic_claims")
    op.drop_table("claims")
    op.drop_table("verification_requests")
    op.execute("DROP EXTENSION IF EXISTS vector;")
