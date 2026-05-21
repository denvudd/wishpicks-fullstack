"""add_image_dimensions_to_wish_items

Revision ID: d4a1f9c2e836
Revises: 2b85e80489b2
Create Date: 2026-05-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4a1f9c2e836'
down_revision: Union[str, None] = '2b85e80489b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('wish_items', sa.Column('image_width', sa.Integer(), nullable=True))
    op.add_column('wish_items', sa.Column('image_height', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('wish_items', 'image_height')
    op.drop_column('wish_items', 'image_width')
