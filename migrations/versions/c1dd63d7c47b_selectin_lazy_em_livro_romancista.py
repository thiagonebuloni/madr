"""selectin lazy em Livro romancista

Revision ID: c1dd63d7c47b
Revises: 48e4bfdf94a2
Create Date: 2025-07-19 08:31:46.780067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1dd63d7c47b'
down_revision: Union[str, Sequence[str], None] = '48e4bfdf94a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
