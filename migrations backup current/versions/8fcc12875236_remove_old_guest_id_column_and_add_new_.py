"""Remove old guest_id column and add new auto-incrementing guest_id

Revision ID: 8fcc12875236
Revises: ea0c0bbf8a79
Create Date: 2024-10-03 16:35:02.232831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fcc12875236'
down_revision = 'ea0c0bbf8a79'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('user_word_pair', 'guest_id')  # Remove old column
    op.add_column('user_word_pair', sa.Column('guest_id', sa.Integer(), autoincrement=True, nullable=True))  # Add new column



def downgrade():
    op.add_column('user_word_pair', sa.Column('guest_id', sa.String(), nullable=True))  # Restore the old column if needed
    op.drop_column('user_word_pair', 'guest_id')  # Remove new column

