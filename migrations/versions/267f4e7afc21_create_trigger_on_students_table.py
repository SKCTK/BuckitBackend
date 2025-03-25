"""Create trigger on students table

Revision ID: 267f4e7afc21
Revises: e91883af6d09
Create Date: 2025-03-25 00:46:56.456971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '267f4e7afc21'
down_revision: Union[str, None] = 'e91883af6d09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
