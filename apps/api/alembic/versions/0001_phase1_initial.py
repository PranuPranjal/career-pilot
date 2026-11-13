from alembic import op
import sqlalchemy as sa
revision = "0001_phase1_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_table("users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("candidate_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("headline", sa.String(300), nullable=False, server_default=""),
        sa.Column("location", sa.String(200), nullable=False, server_default=""),
        sa.Column("experience_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)))
    op.create_table("resumes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("parse_status", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_resumes_tenant_id", "resumes", ["tenant_id"])
    op.create_table("candidate_facts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("resume_id", sa.String(36), sa.ForeignKey("resumes.id")),
        sa.Column("fact_key", sa.String(100), nullable=False),
        sa.Column("fact_value", sa.Text(), nullable=False),
        sa.Column("provenance", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "fact_key", "fact_value", name="uq_candidate_fact"))
    op.create_index("ix_candidate_facts_tenant_id", "candidate_facts", ["tenant_id"])
    op.create_index("ix_candidate_facts_fact_key", "candidate_facts", ["fact_key"])
    op.create_table("onboarding_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_onboarding_messages_tenant_id", "onboarding_messages", ["tenant_id"])

def downgrade():
    op.drop_table("onboarding_messages")
    op.drop_table("candidate_facts")
    op.drop_table("resumes")
    op.drop_table("candidate_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")
    op.drop_table("tenants")
