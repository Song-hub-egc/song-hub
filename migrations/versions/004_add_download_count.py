"""add download_count to dataset

Revision ID: 004
Revises: 003
Create Date: 2025-12-04 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add download_count column to data_set table
    op.add_column('data_set', sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('data_set', 'download_count')
