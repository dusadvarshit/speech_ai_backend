"""Added backref of recordngs into user model

Revision ID: c309d0e523ef
Revises: c9b404222d83
Create Date: 2024-09-23 10:21:27.401126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c309d0e523ef'
down_revision = 'c9b404222d83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recording', schema=None) as batch_op:
        batch_op.alter_column('unique_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recording', schema=None) as batch_op:
        batch_op.alter_column('unique_id',
               existing_type=sa.VARCHAR(length=36),
               nullable=True)

    # ### end Alembic commands ###
