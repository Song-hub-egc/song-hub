"""add cart tables

Revision ID: 005
Revises: 004
Create Date: 2025-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = 'c3982b56aec0'
branch_labels = None
depends_on = None


def upgrade():
    # Create cart table
    op.create_table('cart',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cart_session_id'), 'cart', ['session_id'], unique=False)

    # Create cart_item table
    op.create_table('cart_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('feature_model_id', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], ),
        sa.ForeignKeyConstraint(['feature_model_id'], ['feature_model.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('cart_item')
    op.drop_index(op.f('ix_cart_session_id'), table_name='cart')
    op.drop_table('cart')
