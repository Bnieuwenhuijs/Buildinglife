"""empty message

Revision ID: 1f2de3485b73
Revises: 6dc9e13e0aaa
Create Date: 2019-06-22 21:05:22.583713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f2de3485b73'
down_revision = '6dc9e13e0aaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Building', sa.Column('x_cordinate', sa.String(length=120), nullable=True))
    op.add_column('Building', sa.Column('y_cordinate', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Building', 'y_cordinate')
    op.drop_column('Building', 'x_cordinate')
    # ### end Alembic commands ###
