"""refactor records to separate records and values

Revision ID: abc123def456
Revises: 946c7d1eb4c4
Create Date: 2026-01-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "abc123def456"
down_revision: Union[str, Sequence[str], None] = "946c7d1eb4c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename old records table
    op.rename_table("records", "old_records")

    # Create new records table
    op.create_table(
        "records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "user_scenario_id",
            sa.Integer,
            sa.ForeignKey("user_scenarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    # Create values table
    op.create_table(
        "values",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "record_id",
            sa.Integer,
            sa.ForeignKey("records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.String(150), nullable=False),
        sa.Column(
            "parameter_id",
            sa.Integer,
            sa.ForeignKey("parameters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )

    # Migrate data
    conn = op.get_bind()

    # Insert into records: group by datetime and user_scenario_id
    conn.execute(
        sa.text("""
        INSERT INTO records (created_at, user_scenario_id)
        SELECT DISTINCT r.datetime, p.user_scenario_id
        FROM old_records r
        JOIN parameters p ON r.parameter_id = p.id
        """)
    )

    # Insert into values
    conn.execute(
        sa.text("""
        INSERT INTO values (record_id, value, parameter_id, created_at)
        SELECT rec.id, r.value, r.parameter_id, r.created_at
        FROM old_records r
        JOIN parameters p ON r.parameter_id = p.id
        JOIN records rec ON rec.created_at = r.datetime AND rec.user_scenario_id = p.user_scenario_id
        """)
    )

    # Drop old records table
    op.drop_table("old_records")


def downgrade() -> None:
    """Downgrade schema."""
    # Rename current records to new_records
    op.rename_table("records", "new_records")

    # Recreate old records table
    op.create_table(
        "records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "parameter_id",
            sa.Integer,
            sa.ForeignKey("parameters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("value", sa.String(150), nullable=False),
        sa.Column("datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )

    # Migrate back
    conn = op.get_bind()
    conn.execute(
        sa.text("""
        INSERT INTO records (parameter_id, value, datetime, created_at)
        SELECT v.parameter_id, v.value, r.created_at, v.created_at
        FROM values v
        JOIN new_records r ON v.record_id = r.id
        """)
    )

    # Drop new tables
    op.drop_table("values")
    op.drop_table("new_records")