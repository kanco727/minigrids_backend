"""
Add minigrid_id column to mesure_minigrid
"""
revision = '20231006_add_minigrid_id_to_mesure_minigrid'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
	op.add_column('mesure_minigrid', sa.Column('minigrid_id', sa.Integer(), nullable=True))
	op.create_foreign_key('fk_mesure_minigrid_minigrid_id', 'mesure_minigrid', 'minigrid', ['minigrid_id'], ['id'])

def downgrade():
	# Suppression désactivée pour éviter l’erreur si la contrainte/colonne n’existe pas
	pass
