"""updated Chat and User

Revision ID: 9a5292afa5a0
Revises: 096ee0cce0e0
Create Date: 2025-03-11 11:46:10.309702

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9a5292afa5a0"
down_revision: Union[str, None] = "096ee0cce0e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("chats", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "chats", "users", ["user_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "chats", type_="foreignkey")
    op.drop_column("chats", "user_id")
