"""tipo de notificacao announcement

Escrita à mão: o autogenerate do Alembic não detecta valor novo num ENUM do
PostgreSQL. Sem isto o modelo teria um valor que o banco recusa, e a falha só
apareceria no INSERT — ou seja, no dia em que um edital aparecesse.

Revision ID: d21c9f7a4b16
Revises: 815f5ec57df7
Create Date: 2026-08-11 09:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "d21c9f7a4b16"
down_revision: str | None = "815f5ec57df7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE notification_kind ADD VALUE IF NOT EXISTS 'announcement'")


def downgrade() -> None:
    # O PostgreSQL não remove valor de ENUM. Apagar as linhas que usam o valor é o
    # mais honesto: recriar o tipo perderia as mesmas linhas de qualquer forma.
    op.execute("DELETE FROM notification WHERE kind = 'announcement'")
