"""2024-03_06_Fix user_id type column

Revision ID: 6a3e79453f29
Revises: dfbc31283c36
Create Date: 2024-03-06 02:07:01.367620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6a3e79453f29'
down_revision: Union[str, None] = 'dfbc31283c36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('refunds ', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('refunds ', 'user_id',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
