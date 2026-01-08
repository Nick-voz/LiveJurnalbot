"""model improvements

Revision ID: 946c7d1eb4c4
Revises: 3f34253dc04c
Create Date: 2026-01-04 20:33:39.396885

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "946c7d1eb4c4"
down_revision: Union[str, Sequence[str], None] = "3f34253dc04c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add created_at columns
    op.add_column(
        "scenarios",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )
    op.add_column(
        "reminder_strategies",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )
    op.add_column(
        "user_scenarios",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )
    op.add_column(
        "parametrs",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )
    op.add_column(
        "records",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', NOW())"),
            nullable=False,
        ),
    )

    # Rename table parametrs to parameters
    op.rename_table("parametrs", "parameters")

    # Drop old unique constraint on user_scenarios.scenario_id if it exists
    # Check if constraint exists before dropping
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
        SELECT conname FROM pg_constraint
        WHERE conrelid = 'user_scenarios'::regclass
        AND conname = 'scenario_id'
        AND contype = 'u'
    """
        )
    )
    if result.fetchone():
        op.drop_constraint("scenario_id", "user_scenarios", type_="unique")
    # Add new unique constraint on (user_id, scenario_id)
    op.create_unique_constraint(
        "user_scenarios_user_id_scenario_id_key",
        "user_scenarios",
        ["user_id", "scenario_id"],
    )

    # Update FK in records to point to parameters.id with ondelete CASCADE
    op.drop_constraint("records_parameter_id_fkey", "records", type_="foreignkey")
    op.create_foreign_key(
        "records_parameter_id_fkey",
        "records",
        "parameters",
        ["parameter_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Update FK in parameters.user_scenario_id to add ondelete CASCADE
    op.drop_constraint(
        "parametrs_user_scenario_id_fkey", "parameters", type_="foreignkey"
    )
    op.create_foreign_key(
        "parameters_user_scenario_id_fkey",
        "parameters",
        "user_scenarios",
        ["user_scenario_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Update FK in user_scenarios.scenario_id to add ondelete CASCADE
    op.drop_constraint(
        "user_scenarios_scenario_id_fkey", "user_scenarios", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_scenarios_scenario_id_fkey",
        "user_scenarios",
        "scenarios",
        ["scenario_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
