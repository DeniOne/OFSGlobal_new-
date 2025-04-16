"""add_staff_file_fields

Revision ID: 82f8cfa4d571
Revises: 095344ece7d9
Create Date: 2025-04-16 20:06:42.404297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '82f8cfa4d571'
down_revision: Union[str, None] = '095344ece7d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: добавление полей для хранения файлов сотрудников."""
    # SQLite не поддерживает JSONB, а при миграции на PostgreSQL это будет преобразовано
    op.add_column(
        'staff', 
        sa.Column('photo_path', sa.String(255), nullable=True, comment="Путь к фотографии сотрудника")
    )
    op.add_column(
        'staff', 
        sa.Column('document_paths', postgresql.JSONB(astext_type=sa.Text()), 
                  nullable=True, 
                  server_default='{}',
                  comment="JSON с путями к документам и их типами")
    )


def downgrade() -> None:
    """Downgrade schema: удаление полей для хранения файлов сотрудников."""
    op.drop_column('staff', 'document_paths')
    op.drop_column('staff', 'photo_path')
