"""Remove attempts table and update UserWordPair

Revision ID: 04a5d5f09ab8
Revises: f0652e6f2682
Create Date: 2024-10-07 16:40:07.139254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04a5d5f09ab8'
down_revision = 'f0652e6f2682'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user_word_pair') as batch_op:
        batch_op.alter_column(
            'attempts',
            type_=sa.JSON,
            postgresql_using='attempts::json'
        )


def downgrade():
    # Reverse the upgrade steps
    with op.batch_alter_table('user_word_pair') as batch_op:
        batch_op.alter_column('attempts', type_=sa.Integer(), existing_type=sa.JSON())

    # Recreate the attempts table if necessary
    op.create_table(
        'attempts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('word_pair_id', sa.Integer(), sa.ForeignKey('word_pair.id')),
        sa.Column('attempt_data', sa.JSON())  # Adjust the structure as needed
    )
