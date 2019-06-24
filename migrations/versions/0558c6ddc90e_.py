"""empty message

Revision ID: 0558c6ddc90e
Revises: 2c4563634dc4
Create Date: 2019-06-24 14:19:20.847109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0558c6ddc90e'
down_revision = '2c4563634dc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Building', sa.Column('postal_code', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Building', 'postal_code')
    # ### end Alembic commands ###