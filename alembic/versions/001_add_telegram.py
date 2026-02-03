"""Add telegram_chat_id to User model

Revision ID: 001_add_telegram
Revises: 
Create Date: 2026-02-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_telegram'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add telegram_chat_id column to users table
    op.add_column('users', sa.Column('telegram_chat_id', sa.String(), nullable=True))
    # Create unique index
    op.create_unique_constraint('uq_users_telegram_chat_id', 'users', ['telegram_chat_id'])
    op.create_index('ix_users_telegram_chat_id', 'users', ['telegram_chat_id'])


def downgrade() -> None:
    op.drop_index('ix_users_telegram_chat_id', table_name='users')
    op.drop_constraint('uq_users_telegram_chat_id', 'users', type_='unique')
    op.drop_column('users', 'telegram_chat_id')
