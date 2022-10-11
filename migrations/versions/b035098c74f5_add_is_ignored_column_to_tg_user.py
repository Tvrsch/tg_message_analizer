"""add is_ignored column to tg_user

Revision ID: b035098c74f5
Revises: 0171d349295d
Create Date: 2022-10-10 19:28:28.656741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b035098c74f5'
down_revision = '0171d349295d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tg_user', sa.Column('is_ignored', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tg_user', 'is_ignored')
    # ### end Alembic commands ###