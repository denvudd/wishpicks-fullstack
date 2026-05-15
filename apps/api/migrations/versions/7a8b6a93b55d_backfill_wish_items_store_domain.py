"""backfill_wish_items_store_domain

Revision ID: 7a8b6a93b55d
Revises: c88bcb93f34b
Create Date: 2026-05-10 19:24:33.849953

"""
from typing import Sequence, Union

from alembic import op


revision: str = '7a8b6a93b55d'
down_revision: Union[str, None] = 'c88bcb93f34b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE wish_items
        SET store_domain = regexp_replace(
            regexp_replace(
                regexp_replace(product_url, '^https?://', ''),
                '^www\\.', ''
            ),
            '/.*$', ''
        )
        WHERE product_url IS NOT NULL
          AND product_url != ''
        """
    )


def downgrade() -> None:
    op.execute("UPDATE wish_items SET store_domain = NULL")
