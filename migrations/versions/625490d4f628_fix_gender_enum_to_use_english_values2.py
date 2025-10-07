"""fix_gender_enum_to_use_english_values2

Revision ID: 625490d4f628
Revises: c1238302bb77
Create Date: 2025-10-07 13:43:22.087074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '625490d4f628'
down_revision: Union[str, Sequence[str], None] = 'c1238302bb77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
