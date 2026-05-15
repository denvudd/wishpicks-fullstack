"""wish_item_price_range_notes_tags

Revision ID: b7c3d8e1f204
Revises: a93d6fede7da
Create Date: 2026-05-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b7c3d8e1f204'
down_revision: Union[str, None] = 'a93d6fede7da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('wish_items', 'price', new_column_name='price_min')
    op.add_column('wish_items', sa.Column('price_max', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('wish_items', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('wish_items', sa.Column('tags', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('wish_items', 'tags')
    op.drop_column('wish_items', 'notes')
    op.drop_column('wish_items', 'price_max')
    op.alter_column('wish_items', 'price_min', new_column_name='price')
