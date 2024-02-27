"""Initial

Revision ID: 1583bbb42208
Revises: 
Create Date: 2024-02-27 09:14:17.287054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1583bbb42208'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('features',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('available_entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('features_pkey'))
    )
    op.create_index(op.f('features_name_idx'), 'features', ['name'], unique=False)
    op.create_table('payment_providers',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('payment_providers_pkey'))
    )
    op.create_index(op.f('payment_providers_name_idx'), 'payment_providers', ['name'], unique=False)
    op.create_table('plans',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_recurring', sa.Boolean(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('duration_unit', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('price_per_unit', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('plans_pkey'))
    )
    op.create_index(op.f('plans_name_idx'), 'plans', ['name'], unique=False)
    op.create_table('planstofeatureslink',
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('feature_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['feature_id'], ['features.id'], name=op.f('planstofeatureslink_feature_id_fkey')),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('planstofeatureslink_plan_id_fkey')),
    sa.PrimaryKeyConstraint('plan_id', 'feature_id', name=op.f('planstofeatureslink_pkey'))
    )
    op.create_table('subscriptions',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'ACTIVE', 'EXPIRED', 'CANCELED', 'PAUSED', name='subscriptionstatusenum'), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('ended_at', sa.DateTime(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('subscriptions_plan_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('subscriptions_pkey'))
    )
    op.create_index(op.f('subscriptions_name_idx'), 'subscriptions', ['name'], unique=False)
    op.create_index(op.f('subscriptions_user_id_idx'), 'subscriptions', ['user_id'], unique=False)
    op.create_table('payments',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('payment_provider_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('CREATED', 'PENDING', 'PAID', 'EXPIRED', 'CANCELED', name='paymentstatusenum'), nullable=False),
    sa.Column('currency', sa.Enum('RUB', 'USD', 'EUR', name='currencyenum'), nullable=False),
    sa.Column('amount', sa.Numeric(precision=8, scale=2), nullable=False),
    sa.CheckConstraint('amount > 0', name=op.f('payments_amount_positive_integer_check')),
    sa.ForeignKeyConstraint(['payment_provider_id'], ['payment_providers.id'], name=op.f('payments_payment_provider_id_fkey')),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], name=op.f('payments_subscription_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('payments_pkey'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payments')
    op.drop_index(op.f('subscriptions_user_id_idx'), table_name='subscriptions')
    op.drop_index(op.f('subscriptions_name_idx'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_table('planstofeatureslink')
    op.drop_index(op.f('plans_name_idx'), table_name='plans')
    op.drop_table('plans')
    op.drop_index(op.f('payment_providers_name_idx'), table_name='payment_providers')
    op.drop_table('payment_providers')
    op.drop_index(op.f('features_name_idx'), table_name='features')
    op.drop_table('features')
    # ### end Alembic commands ###