"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'runs',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('cmd', sa.Text()),
        sa.Column('exit_code', sa.Integer()),
        sa.Column('stdout', sa.Text()),
        sa.Column('parsed', sa.JSON()),
    )

    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
    )

    op.create_table(
        'providers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('encrypted_secret', sa.Text()),
    )

    op.create_table(
        'webhook_queue',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('webhook_id', sa.Integer()),
        sa.Column('run_id', sa.String(length=64)),
        sa.Column('attempts', sa.Integer(), server_default='0'),
        sa.Column('next_try', sa.DateTime()),
    )

    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('webhook_id', sa.Integer()),
        sa.Column('run_id', sa.String(length=64)),
        sa.Column('status_code', sa.Integer()),
        sa.Column('response', sa.Text()),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('ts', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actor', sa.String(length=128)),
        sa.Column('action', sa.String(length=256)),
        sa.Column('details', sa.Text()),
    )


def downgrade():
    op.drop_table('webhook_deliveries')
    op.drop_table('webhook_queue')
    op.drop_table('providers')
    op.drop_table('webhooks')
    op.drop_table('runs')
