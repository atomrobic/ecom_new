"""Add categories and category_id to products

Revision ID: b602e714e4a0
Revises: a0efcdc9e81f
Create Date: 2025-08-20 16:37:36.775219
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'b602e714e4a0'
down_revision = 'a0efcdc9e81f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Only create categories table if it doesn't exist
    if 'categories' not in inspector.get_table_names():
        op.create_table(
            'categories',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, nullable=False, unique=True),
        )

    # Add category_id column to products if it doesn't exist
    if 'category_id' not in [col['name'] for col in inspector.get_columns('products')]:
        op.add_column('products', sa.Column('category_id', sa.Integer, nullable=True))
        op.create_foreign_key(
            'products_category_id_fkey',
            'products',
            'categories',
            ['category_id'],
            ['id'],
            ondelete="SET NULL"
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Drop foreign key if exists
    fkeys = [fk['name'] for fk in inspector.get_foreign_keys('products')]
    if 'products_category_id_fkey' in fkeys:
        op.drop_constraint('products_category_id_fkey', 'products', type_='foreignkey')

    # Drop column if exists
    columns = [col['name'] for col in inspector.get_columns('products')]
    if 'category_id' in columns:
        op.drop_column('products', 'category_id')

    # Drop table if exists
    if 'categories' in inspector.get_table_names():
        op.drop_table('categories')
