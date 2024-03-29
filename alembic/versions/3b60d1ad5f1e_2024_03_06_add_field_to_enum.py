"""2024-03_06_Add field to enum

Revision ID: 3b60d1ad5f1e
Revises: 7c986d3848f2
Create Date: 2024-03-06 00:49:38.665411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b60d1ad5f1e'
down_revision: Union[str, None] = '7c986d3848f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE subscriptionstatusenum ADD VALUE 'DELETED'")
    op.execute("ALTER TYPE paymentstatusenum ADD VALUE 'REFUNDED'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("UPDATE subscriptions SET status = null WHERE status = 'DELETED'")
    op.execute("ALTER TABLE subscriptions ALTER status TYPE text")
    op.execute("DROP TYPE subscriptionstatusenum")
    op.execute("CREATE TYPE subscriptionstatusenum AS enum('CREATED', 'ACTIVE', 'EXPIRED', 'CANCELED', 'PAUSED')")
    op.execute("ALTER TABLE subscriptions ALTER status TYPE subscriptionstatusenum using status::subscriptionstatusenum")

    op.execute("UPDATE payments SET status = null WHERE status = 'REFUNDED'")
    op.execute("ALTER TABLE payments ALTER status TYPE text")
    op.execute("DROP TYPE payments")
    op.execute("CREATE TYPE paymentstatusenum AS enum('CREATED', 'PENDING', 'PAID', 'EXPIRED', 'CANCELED')")
    op.execute("ALTER TABLE payments ALTER status TYPE paymentstatusenum using status::paymentstatusenum")
    # ### end Alembic commands ###
