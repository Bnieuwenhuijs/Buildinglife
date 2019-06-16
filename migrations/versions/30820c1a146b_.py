"""empty message

Revision ID: 30820c1a146b
Revises: 
Create Date: 2019-06-15 18:35:00.884328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30820c1a146b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('surname', sa.String(length=120), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('Building',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('building_year', sa.Integer(), nullable=True),
    sa.Column('building_functionality', sa.String(length=120), nullable=True),
    sa.Column('square_meters', sa.Float(), nullable=True),
    sa.Column('number_floors', sa.Integer(), nullable=True),
    sa.Column('total_value', sa.Integer(), nullable=True),
    sa.Column('steel_quantity', sa.Integer(), nullable=True),
    sa.Column('steel_Value', sa.Integer(), nullable=True),
    sa.Column('copper_quantity', sa.Integer(), nullable=True),
    sa.Column('copper_Value', sa.Integer(), nullable=True),
    sa.Column('concrete_quantity', sa.Integer(), nullable=True),
    sa.Column('concrete_Value', sa.Integer(), nullable=True),
    sa.Column('timber_quantity', sa.Integer(), nullable=True),
    sa.Column('timber_Value', sa.Integer(), nullable=True),
    sa.Column('glass_quantity', sa.Integer(), nullable=True),
    sa.Column('glass_Value', sa.Integer(), nullable=True),
    sa.Column('polystyrene_quantity', sa.Integer(), nullable=True),
    sa.Column('polystyrene_Value', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('license',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('license_hash', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('license_type', sa.String(length=13), nullable=True),
    sa.Column('isActive', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('license')
    op.drop_table('Building')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
