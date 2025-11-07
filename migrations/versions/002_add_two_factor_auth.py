"""add two factor authentication

Revision ID: 002
Revises: 001
Create Date: 2025-11-04 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('two_factor_secret', sa.String(length=32), nullable=True))
    op.add_column('user', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('backup_codes', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('user', 'backup_codes')
    op.drop_column('user', 'two_factor_enabled')
    op.drop_column('user', 'two_factor_secret')
