"""email_unsubscribe_token

Revision ID: 47af4ae00ca3
Revises: 72b80fb37c75
Create Date: 2024-04-16 20:16:43.357263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47af4ae00ca3'
down_revision = '72b80fb37c75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_unsubscribe_token', sa.String(), nullable=False,
                                      server_default="placeholder"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('email_unsubscribe_token')

    # ### end Alembic commands ###
