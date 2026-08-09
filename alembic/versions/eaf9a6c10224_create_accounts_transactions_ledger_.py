"""create accounts transactions ledger_entries tables

Revision ID: eaf9a6c10224
Revises: 
Create Date: 2026-07-04 17:19:39.538639

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaf9a6c10224'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_name', sa.String(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_accounts_id', 'accounts', ['id'])

    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('idempotency_key', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transactions_id', 'transactions', ['id'])
    op.create_index('ix_transactions_idempotency_key', 'transactions', ['idempotency_key'], unique=True)

    op.create_table('ledger_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('entry_type', sa.Enum('DEBIT', 'CREDIT', name='entrytype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ledger_entries_id', 'ledger_entries', ['id'])


def downgrade() -> None:
    op.drop_table('ledger_entries')
    op.drop_table('transactions')
    op.drop_table('accounts')
