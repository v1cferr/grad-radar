"""fonte sabe de qual programa fala

Revision ID: e6319f5b4c0b
Revises: 4b448abc1d94
Create Date: 2026-08-10 19:53:37.462350
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'e6319f5b4c0b'
down_revision: str | None = '4b448abc1d94'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# A FK é NOMEADA à mão. O autogenerate emite `create_foreign_key(None, ...)` e o
# downgrade correspondente vira `drop_constraint(None, ...)`, que explode com
# "it has no name" — um downgrade que não desfaz, e que só falha quando alguém
# precisa dele. Terceira vez que esta classe de bug aparece neste repositório.
FK = "fk_source_program_id_graduate_program"


def upgrade() -> None:
    op.add_column("source", sa.Column("program_id", sa.Integer(), nullable=True))
    op.create_foreign_key(FK, "source", "graduate_program", ["program_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FK, "source", type_="foreignkey")
    op.drop_column("source", "program_id")
