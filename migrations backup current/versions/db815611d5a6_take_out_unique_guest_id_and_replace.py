"""take out unique_guest_id and replace

Revision ID: db815611d5a6
Revises: 52feb79dd8b6
Create Date: 2024-10-04 14:07:48.648525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db815611d5a6'
down_revision = '52feb79dd8b6'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    #with op.batch_alter_table('guest', schema=None) as batch_op:
    #    batch_op.drop_constraint('guest_unique_guest_id_key', type_='unique')
    #    batch_op.drop_column('unique_guest_id')

    # ### end Alembic commands ###


def downgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    #with op.batch_alter_table('guest', schema=None) as batch_op:
    #    batch_op.add_column(sa.Column('unique_guest_id', sa.INTEGER(), autoincrement=False, nullable=False))
    #    batch_op.create_unique_constraint('guest_unique_guest_id_key', ['unique_guest_id'])

    # ### end Alembic commands ###
