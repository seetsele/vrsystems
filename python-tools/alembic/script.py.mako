%!
from alembic import util

revision = context.get_x_argument(as_dictionary=True).get('rev')

def render_imports():
    return ''

"""
Revision script template.
"""
__doc__ = """"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
"""
Auto-generated Alembic script template
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    pass

def downgrade():
    pass
