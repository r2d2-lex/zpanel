"""Fix table

Revision ID: d8661a8115c2
Revises: f1f8dbfd102d
Create Date: 2023-05-25 09:13:53.497598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8661a8115c2'
down_revision = 'f1f8dbfd102d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('item_host_id_fkey', 'item', type_='foreignkey')
    op.create_foreign_key(None, 'item', 'host', ['host_id'], ['host_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.create_foreign_key('item_host_id_fkey', 'item', 'host', ['host_id'], ['host_id'])
    # ### end Alembic commands ###
