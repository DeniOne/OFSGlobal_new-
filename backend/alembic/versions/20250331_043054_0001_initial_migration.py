"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2025-03-31 04:30:54.481784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('org_type', sa.String(length=20), nullable=False),
        sa.Column('ckp', sa.String(length=500), nullable=True),
        sa.Column('inn', sa.String(length=12), nullable=True),
        sa.Column('kpp', sa.String(length=9), nullable=True),
        sa.Column('legal_address', sa.String(length=500), nullable=True),
        sa.Column('physical_address', sa.String(length=500), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )
    # Создаем индексы
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_is_active'), 'organizations', ['is_active'], unique=False)
    op.create_index(op.f('ix_organizations_inn'), 'organizations', ['inn'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_org_type'), 'organizations', ['org_type'], unique=False)
    op.create_index(op.f('ix_organizations_parent_id'), 'organizations', ['parent_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индексы
    op.drop_index(op.f('ix_organizations_parent_id'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_org_type'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_inn'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_is_active'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    # Удаляем таблицу
    op.drop_table('organizations')
