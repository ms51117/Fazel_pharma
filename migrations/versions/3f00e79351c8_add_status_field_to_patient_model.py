"""add_status_field_to_patient_model

Revision ID: 3f00e79351c8
Revises: 89654b79b64b
Create Date: 2025-10-27 12:04:14.498838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '3f00e79351c8'
down_revision: Union[str, Sequence[str], None] = '89654b79b64b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# تعریف شیء Enum در سطح ماژول (این بخش در کد شما درست بود)
patient_status_enum = sa.Enum(
    'AWAITING_PROFILE_COMPLETION',
    'PROFILE_COMPLETED',
    'AWAITING_CONSULTATION',
    'AWAITING_INVOICE_APPROVAL',
    'AWAITING_PAYMENT',
    'PAYMENT_COMPLETED',
    'PAYMENT_CONFIRMED',
    'AWAITING_SHIPMENT',
    'SHIPPED',
    'COMPLETED',
    'CANCELLED',
    name='patientstatus'
)


def upgrade() -> None:
    """Upgrade schema."""
    # ### شروع تغییرات ###

    # مرحله ۱: نوع ENUM را در دیتابیس PostgreSQL ایجاد کن.
    patient_status_enum.create(op.get_bind())

    # مرحله ۲: ستون را با استفاده از نوع ایجاد شده و یک مقدار پیش‌فرض اضافه کن.
    # نکته: نام ستون شما در مدل 'patient_status' است، پس اینجا هم باید 'patient_status' باشد.
    op.add_column('tbl_Patient', sa.Column('patient_status', patient_status_enum, nullable=False,
                                           server_default='AWAITING_PROFILE_COMPLETION'))

    # مرحله ۳: ایندکس را ایجاد کن (این بخش در کد شما صحیح بود).
    op.create_index(op.f('ix_tbl_Patient_patient_status'), 'tbl_Patient', ['patient_status'], unique=False)

    # ### پایان تغییرات ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### شروع تغییرات ###

    # مرحله ۱: ایندکس را حذف کن.
    op.drop_index(op.f('ix_tbl_Patient_patient_status'), table_name='tbl_Patient')

    # مرحله ۲: ستون را حذف کن.
    op.drop_column('tbl_Patient', 'patient_status')

    # مرحله ۳: نوع ENUM را از دیتابیس PostgreSQL حذف کن.
    patient_status_enum.drop(op.get_bind())

    # ### پایان تغییرات ###
