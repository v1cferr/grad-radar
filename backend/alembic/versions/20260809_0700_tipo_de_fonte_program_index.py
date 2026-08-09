"""tipo de fonte program_index

Escrita à mão: o autogenerate do Alembic não detecta valores novos num ENUM do
PostgreSQL — ele compara tabelas e colunas, não o conteúdo dos tipos. Sem esta
migração o modelo teria um valor que o banco recusa, e a falha só apareceria no
INSERT.

Revision ID: c14a7f2e9b03
Revises: 8fb2b1dfdc68
Create Date: 2026-08-09 07:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "c14a7f2e9b03"
down_revision: str | None = "8fb2b1dfdc68"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ADD VALUE não roda dentro de um bloco transacional no PostgreSQL antigo;
    # do 12 em diante roda, e o compose fixa o 17. IF NOT EXISTS torna a
    # migração repetível sem erro.
    op.execute("ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'program_index'")


def downgrade() -> None:
    # O PostgreSQL não remove valor de ENUM. Reverter de verdade exigiria
    # recriar o tipo e reescrever a coluna; as fontes que usam este valor seriam
    # perdidas de qualquer jeito. Apagá-las é o mais honesto que dá para fazer,
    # e é reversível re-rodando o seed.
    op.execute("DELETE FROM source_snapshot WHERE source_id IN "
               "(SELECT id FROM source WHERE source_type = 'program_index')")
    op.execute("DELETE FROM source WHERE source_type = 'program_index'")
