"""Add hints_used column to UserWordPair

Revision ID: b820dc4435da
Revises: c7779b654b7e
Create Date: 2024-09-30 20:16:32.810036

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b820dc4435da'
down_revision = 'c7779b654b7e'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Add the column as nullable
    op.add_column('user_word_pair', sa.Column('hints_used', sa.Integer(), nullable=True))

    # Step 2: Update existing rows to set a default value
    op.execute("UPDATE user_word_pair SET hints_used = 0 WHERE hints_used IS NULL")

    # Step 3: Alter the column to be NOT NULL
    op.alter_column('user_word_pair', 'hints_used', existing_type=sa.Integer(), nullable=False)

def downgrade():
    op.drop_column('user_word_pair', 'hints_used')
