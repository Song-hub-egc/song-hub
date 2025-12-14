"""Merge image cart support with existing migrations

Revision ID: a953b1fc1a78
Revises: 011, 2bb8e9f66865
Create Date: 2025-12-14 22:42:08.816531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a953b1fc1a78'
down_revision = ('011', '2bb8e9f66865')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
