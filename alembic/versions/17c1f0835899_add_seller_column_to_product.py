"""Add seller column to product

Revision ID: 17c1f0835899
Revises: 48e610cf4cba
Create Date: 2025-08-09 08:57:57.452774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17c1f0835899'
down_revision: Union[str, Sequence[str], None] = '48e610cf4cba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('seller_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_products_seller_id',  # Name of the constraint
        'products',               # Source table
        'sellers',                 # Referenced table
        ['seller_id'],             # Column in products
        ['id']                     # Column in sellers
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_products_seller_id', 'products', type_='foreignkey')
    op.drop_column('products', 'seller_id')