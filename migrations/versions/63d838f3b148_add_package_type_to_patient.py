"""add_package_type_to_patient

Revision ID: 63d838f3b148
Revises: 1eac10def8e6
Create Date: 2025-12-07 14:18:18.875917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql  # <--- این خط اضافه شد


# revision identifiers, used by Alembic.
revision: str = '63d838f3b148'
down_revision: Union[str, Sequence[str], None] = '1eac10def8e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. ابتدا نوع Enum را در دیتابیس پستگرس می‌سازیم
    package_type_enum = postgresql.ENUM('ECONOMIC', 'PREMIUM', name='packagetypeenum')
    package_type_enum.create(op.get_bind())

    # 2. سپس ستون را اضافه می‌کنیم
    op.add_column('tbl_Patient', sa.Column('package_type', sa.Enum('ECONOMIC', 'PREMIUM', name='packagetypeenum'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # 1. ابتدا ستون را حذف می‌کنیم
    op.drop_column('tbl_Patient', 'package_type')

    # 2. سپس نوع Enum را از دیتابیس پاک می‌کنیم
    package_type_enum = postgresql.ENUM('ECONOMIC', 'PREMIUM', name='packagetypeenum')
    package_type_enum.drop(op.get_bind())