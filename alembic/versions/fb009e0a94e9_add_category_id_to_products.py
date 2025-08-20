"""Add category_id to products

Revision ID: fb009e0a94e9
Revises: b602e714e4a0
Create Date: 2025-08-21 00:40:11.681891
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fb009e0a94e9'
down_revision = 'b602e714e4a0'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add category_id column to products table."""
    op.add_column('products', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_products_category',  # constraint name
        'products',              # source table
        'categories',            # target table
        ['category_id'],         # source column
        ['id']                   # target column
    )

def downgrade() -> None:
    """Remove category_id column from products table."""
    op.drop_constraint('fk_products_category', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
