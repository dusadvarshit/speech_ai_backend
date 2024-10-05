"""Added the feedback text component to database itself

Revision ID: 146f7f16b300
Revises: d2245a30b13a
Create Date: 2024-10-05 07:40:48.979303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '146f7f16b300'
down_revision = 'd2245a30b13a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recording', schema=None) as batch_op:
        batch_op.add_column(sa.Column('audio_signal_feedback', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recording', schema=None) as batch_op:
        batch_op.drop_column('audio_signal_feedback')

    # ### end Alembic commands ###
