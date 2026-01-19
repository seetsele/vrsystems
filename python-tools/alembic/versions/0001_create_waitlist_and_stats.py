"""create waitlist and stats tables

Revision ID: 0001_create_waitlist_and_stats
Revises: 
Create Date: 2026-01-18 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_waitlist_and_stats'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table('waitlist'):
        op.create_table(
            'waitlist',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('email', sa.Text(), nullable=False),
            sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

    if not inspector.has_table('stats'):
        op.create_table(
            'stats',
            sa.Column('key', sa.Text(), primary_key=True),
            sa.Column('value', sa.JSON()),
        )


def downgrade():
    op.drop_table('stats')
    op.drop_table('waitlist')
