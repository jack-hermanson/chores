"""ListAccount

Revision ID: ff6bcf348e67
Revises: ed462923ae0a
Create Date: 2023-09-10 15:00:21.536538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff6bcf348e67'
down_revision = 'ed462923ae0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('list_account',
    sa.Column('list_id', sa.Integer(), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.account_id'], ),
    sa.ForeignKeyConstraint(['list_id'], ['list.list_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('list_account')
    # ### end Alembic commands ###
