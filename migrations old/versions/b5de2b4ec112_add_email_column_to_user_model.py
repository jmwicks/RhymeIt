"""Add email column to User model

Revision ID: b5de2b4ec112
Revises: 
Create Date: 2024-08-15 19:42:28.378872

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b5de2b4ec112'  # Make sure this is correct
down_revision = None # Make sure this is correct
branch_labels = None
depends_on = None

def upgrade():
    # Add the email column to the user table
    op.add_column('user', sa.Column('email', sa.String(length=120), nullable=False, unique=True))

def downgrade():
    # Remove the email column from the user table
    op.drop_column('user', 'email')


