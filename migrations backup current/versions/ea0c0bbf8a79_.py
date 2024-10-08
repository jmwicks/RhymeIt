"""empty message

Revision ID: ea0c0bbf8a79
Revises: 838b6cda8771
Create Date: 2024-10-03 16:32:48.341733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea0c0bbf8a79'
down_revision = '838b6cda8771'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user_word_pair', 'guest_id',
        existing_type=sa.Integer(),
        nullable=True,
        autoincrement=True)

def downgrade():
    op.alter_column('user_word_pair', 'guest_id',
        existing_type=sa.Integer(),
        nullable=True)


    # ### end Alembic commands ###
