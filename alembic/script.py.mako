<%doc>
    Alembic migration script template
</%doc>
"""${message}

Revision ID: ${up_revision}
Revises: ${', '.join(down_revisions)}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${repr(down_revisions) if len(down_revisions) > 1 else repr(down_revisions[0])}
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
