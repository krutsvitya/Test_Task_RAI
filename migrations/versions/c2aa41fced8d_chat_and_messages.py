"""Chat and Messages

Revision ID: c2aa41fced8d
Revises: 905f3bc42a08
Create Date: 2025-03-10 18:54:07.366232

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2aa41fced8d"
down_revision: Union[str, None] = "905f3bc42a08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chats_id"), "chats", ["id"], unique=False)
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["chat_id"],
            ["chats.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_chats_id"), table_name="chats")
    op.drop_table("chats")
