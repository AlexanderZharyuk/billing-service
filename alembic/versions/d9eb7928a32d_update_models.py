"""Update models

Revision ID: d9eb7928a32d
Revises: f04722eb4805
Create Date: 2024-03-02 19:00:41.025251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd9eb7928a32d'
down_revision: Union[str, None] = 'f04722eb4805'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('BANK_CARD', 'YOO_MONEY', 'SBERBANK', 'TINKOFF_BANK', 'SBP', name='paymentmethodsenum').create(op.get_bind(), checkfirst=True)
    op.create_table('prices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('currency', postgresql.ENUM('RUB', 'USD', 'EUR', name='currencyenum', create_type=False), nullable=True),
    sa.Column('amount', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('prices_plan_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('prices_pkey'))
    )
    op.add_column('payments', sa.Column('payment_method', sa.Enum('BANK_CARD', 'YOO_MONEY', 'SBERBANK', 'TINKOFF_BANK', 'SBP', name='paymentmethodsenum'), nullable=True))
    op.add_column('payments', sa.Column('external_payment_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('payments', sa.Column('external_payment_type_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('payments', 'status',
               existing_type=postgresql.ENUM('CREATED', 'PENDING', 'PAID', 'EXPIRED', 'CANCELED', name='paymentstatusenum'),
               nullable=True)
    op.alter_column('payments', 'currency',
               existing_type=postgresql.ENUM('RUB', 'USD', 'EUR', name='currencyenum'),
               nullable=True)
    op.create_unique_constraint(op.f('payments_external_payment_id_key'), 'payments', ['external_payment_id'])
    op.drop_constraint('payments_subscription_id_fkey', 'payments', type_='foreignkey')
    op.drop_column('payments', 'subscription_id')
    op.drop_column('payments', 'actual_payment_id')
    op.drop_column('plans', 'price_per_unit')
    op.add_column('subscriptions', sa.Column('payment_id', sa.Integer(), nullable=False))
    op.alter_column('subscriptions', 'status',
               existing_type=postgresql.ENUM('CREATED', 'ACTIVE', 'EXPIRED', 'CANCELED', 'PAUSED', name='subscriptionstatusenum'),
               nullable=True)
    op.drop_index('subscriptions_name_idx', table_name='subscriptions')
    op.create_foreign_key(op.f('subscriptions_payment_id_fkey'), 'subscriptions', 'payments', ['payment_id'], ['id'])
    op.drop_column('subscriptions', 'name')
    op.drop_column('subscriptions', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('subscriptions', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(op.f('subscriptions_payment_id_fkey'), 'subscriptions', type_='foreignkey')
    op.create_index('subscriptions_name_idx', 'subscriptions', ['name'], unique=False)
    op.alter_column('subscriptions', 'status',
               existing_type=postgresql.ENUM('CREATED', 'ACTIVE', 'EXPIRED', 'CANCELED', 'PAUSED', name='subscriptionstatusenum', create_type=False),
               nullable=False)
    op.drop_column('subscriptions', 'payment_id')
    op.add_column('plans', sa.Column('price_per_unit', sa.NUMERIC(precision=8, scale=2), autoincrement=False, nullable=False))
    op.add_column('payments', sa.Column('actual_payment_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('payments', sa.Column('subscription_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('payments_subscription_id_fkey', 'payments', 'subscriptions', ['subscription_id'], ['id'])
    op.drop_constraint(op.f('payments_external_payment_id_key'), 'payments', type_='unique')
    op.alter_column('payments', 'currency',
               existing_type=postgresql.ENUM('RUB', 'USD', 'EUR', name='currencyenum', create_type=False),
               nullable=False)
    op.alter_column('payments', 'status',
               existing_type=postgresql.ENUM('CREATED', 'PENDING', 'PAID', 'EXPIRED', 'CANCELED', name='paymentstatusenum', create_type=False),
               nullable=False)
    op.drop_column('payments', 'external_payment_type_id')
    op.drop_column('payments', 'external_payment_id')
    op.drop_column('payments', 'payment_method')
    op.drop_table('prices')
    # ### end Alembic commands ###