"""updated Chat and Messages

Revision ID: 096ee0cce0e0
Revises: c2aa41fced8d
Create Date: 2025-03-11 10:08:32.850215

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "096ee0cce0e0"
down_revision: Union[str, None] = "c2aa41fced8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
