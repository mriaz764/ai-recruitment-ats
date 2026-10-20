"""rename user name to full_name

Revision ID: 9b335856dabc
Revises: 30e44f9259ce
Create Date: 2026-10-20 13:21:34.949749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b335856dabc'
down_revision: Union[str, Sequence[str], None] = '30e44f9259ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'name', new_column_name='full_name')

def downgrade() -> None:
    op.alter_column('users', 'full_name', new_column_name='name')
