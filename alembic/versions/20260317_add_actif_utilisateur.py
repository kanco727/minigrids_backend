"""
Migration Alembic : Ajout colonne 'actif' à la table utilisateur
"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '20260317_add_actif_utilisateur'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('utilisateur', sa.Column('actif', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.add_column('utilisateur', sa.Column('date_modification', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    op.drop_column('utilisateur', 'actif')
    op.drop_column('utilisateur', 'date_modification')
