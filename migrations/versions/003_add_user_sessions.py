"""add user sessions

Revision ID: 003
Revises: 002
Create Date: 2025-11-10 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'user_session' not in inspector.get_table_names():
        op.create_table('user_session',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.String(length=255), nullable=False),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('device_type', sa.String(length=50), nullable=True),
            sa.Column('browser', sa.String(length=100), nullable=True),
            sa.Column('os', sa.String(length=100), nullable=True),
            sa.Column('location', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('last_activity', sa.DateTime(), nullable=False),
            sa.Column('is_current', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('session_id')
        )
        op.create_index('idx_user_sessions', 'user_session', ['user_id', 'last_activity'])

    if 'flask_sessions' not in inspector.get_table_names():
        op.create_table('flask_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.String(length=255), nullable=False),
            sa.Column('data', sa.LargeBinary(), nullable=True),
            sa.Column('expiry', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('session_id')
        )


def downgrade():
    op.drop_index('idx_user_sessions', table_name='user_session')
    op.drop_table('user_session')
    op.drop_table('flask_sessions')