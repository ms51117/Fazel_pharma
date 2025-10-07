"""test change

Revision ID: bc2b41a14ca8
Revises: 625490d4f628
Create Date: 2025-10-07 14:27:47.180150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bc2b41a14ca8'
down_revision: Union[str, Sequence[str], None] = '625490d4f628'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ایجاد enum جدید
    gender_enum = sa.Enum('MALE', 'FEMALE', 'UNKNOWN', name='genderenum')
    gender_enum.create(op.get_bind(), checkfirst=True)

    # 2. تبدیل ستون با استفاده از USING
    op.execute("""
        ALTER TABLE "tbl_Patient"
        ALTER COLUMN sex TYPE genderenum
        USING CASE
            WHEN sex = 'male' THEN 'MALE'::genderenum
            WHEN sex = 'female' THEN 'FEMALE'::genderenum
            ELSE 'UNKNOWN'::genderenum
        END
    """)


def downgrade() -> None:
    # 1. برگرداندن ستون به VARCHAR
    op.execute("""
        ALTER TABLE "tbl_Patient"
        ALTER COLUMN sex TYPE VARCHAR
        USING sex::VARCHAR
    """)

    # 2. حذف enum
    gender_enum = sa.Enum('MALE', 'FEMALE', 'UNKNOWN', name='genderenum')
    gender_enum.drop(op.get_bind(), checkfirst=True)