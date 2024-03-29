"""2024-03_06_Remove unique contraint from external_payment_id

Revision ID: 19b28d1fa6cf
Revises: ae7af795a9f6
Create Date: 2024-03-06 20:38:27.339594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19b28d1fa6cf'
down_revision: Union[str, None] = 'ae7af795a9f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('payments_external_payment_id_key', 'payments', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('payments_external_payment_id_key', 'payments', ['external_payment_id'])
    # ### end Alembic commands ###
