"""added module status

Revision ID: 64a4a9796cd6
Revises: 90bc500d8c5f
Create Date: 2024-06-21 00:03:33.341049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64a4a9796cd6'
down_revision: Union[str, None] = '90bc500d8c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('modules', 'on',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('modules', 'on',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
