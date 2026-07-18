"""Initial schema."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("language", sa.String(8), server_default="en"),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=True),
        sa.Column(
            "notify_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
        ),
        sa.Column(
            "plan",
            sa.Enum("free", "premium", name="plantype"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_external_id", "users", ["external_id"], unique=True)
    op.create_index("ix_users_channel", "users", ["channel"])

    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "is_crisis",
            sa.Boolean(),
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_encrypted",
            sa.Boolean(),
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_messages_user_id", "messages", ["user_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])

    op.create_table(
        "event_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("channel", sa.String(32), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("actor", sa.String(64), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_event_logs_event_type", "event_logs", ["event_type"])
    op.create_index("ix_event_logs_user_id", "event_logs", ["user_id"])
    op.create_index("ix_event_logs_created_at", "event_logs", ["created_at"])

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor", sa.String(64), nullable=False),
        sa.Column("target", sa.String(128), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_admin_audit_logs_action",
        "admin_audit_logs",
        ["action"],
    )
    op.create_index(
        "ix_admin_audit_logs_created_at",
        "admin_audit_logs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("event_logs")
    op.drop_table("messages")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS plantype")
