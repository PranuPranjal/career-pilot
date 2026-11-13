from alembic import op
import sqlalchemy as sa
revision = "0002_phase2_jobs"
down_revision = "0001_phase1_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("job_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("board_token", sa.String(300), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_sync_at", sa.DateTime(timezone=True)),
        sa.Column("last_sync_status", sa.String(30), nullable=False, server_default="never_synced"),
        sa.Column("last_sync_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_job_sources_provider", "job_sources", ["provider"])
    op.create_unique_constraint("uq_job_source_provider_board", "job_sources", ["provider", "board_token"])
    op.create_table("job_postings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("job_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(300), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("location", sa.String(500), nullable=False, server_default=""),
        sa.Column("department", sa.String(200), nullable=False, server_default=""),
        sa.Column("employment_type", sa.String(80), nullable=False, server_default=""),
        sa.Column("workplace_type", sa.String(40), nullable=False, server_default=""),
        sa.Column("description_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("description_html", sa.Text(), nullable=False, server_default=""),
        sa.Column("job_url", sa.String(2000), nullable=False),
        sa.Column("apply_url", sa.String(2000), nullable=False, server_default=""),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("source_updated_at", sa.DateTime(timezone=True)),
        sa.Column("content_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "external_id", name="uq_job_source_external"))
    for name, column in [("ix_job_postings_source_id", "source_id"), ("ix_job_postings_title", "title"), ("ix_job_postings_company_name", "company_name"), ("ix_job_postings_location", "location"), ("ix_job_postings_status", "status")]:
        op.create_index(name, "job_postings", [column])

def downgrade():
    op.drop_table("job_postings")
    op.drop_index("ix_job_sources_provider", table_name="job_sources")
    op.drop_table("job_sources")
