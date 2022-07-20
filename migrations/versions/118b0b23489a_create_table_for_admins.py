"""Create table for admins

Revision ID: 118b0b23489a
Revises: f79f5ed0a80f
Create Date: 2022-07-17 17:17:59.626404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '118b0b23489a'
down_revision = 'f79f5ed0a80f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_room_admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('chat_room_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['chat_room_id'], ['chat_room.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('chat_room', sa.Column('is_public', sa.Boolean(), nullable=True))
    op.drop_constraint('chat_room_user_chat_room_id_fkey', 'chat_room_user', type_='foreignkey')
    op.create_foreign_key(None, 'chat_room_user', 'chat_room', ['chat_room_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chat_room_user', type_='foreignkey')
    op.create_foreign_key('chat_room_user_chat_room_id_fkey', 'chat_room_user', 'chat_room', ['chat_room_id'], ['id'])
    op.drop_column('chat_room', 'is_public')
    op.drop_table('chat_room_admin')
    # ### end Alembic commands ###