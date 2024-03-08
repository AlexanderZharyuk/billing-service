"""2024-03_06_Add refunds tables

Revision ID: dfbc31283c36
Revises: 3b60d1ad5f1e
Create Date: 2024-03-06 02:02:11.607720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'dfbc31283c36'
down_revision: Union[str, None] = '3b60d1ad5f1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('refund_reasons',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('refund_reasons_pkey'))
    )
    op.create_table('refunds ',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reason_id', sa.Integer(), nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('additional_info', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['reason_id'], ['refund_reasons.id'], name=op.f('refunds _reason_id_fkey')),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], name=op.f('refunds _subscription_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('refunds _pkey'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('refunds ')
    op.drop_table('refund_reasons')
    # ### end Alembic commands ###