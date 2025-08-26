"""simple parasite preventions table

Revision ID: simple_parasite
Revises: simple_vaccs
Create Date: 2025-08-26 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'simple_parasite'
down_revision = 'simple_vaccs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create parasite_preventions table only
    op.create_table('parasite_preventions',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('dog_id', sa.String(length=255), nullable=False),
    sa.Column('product_name', sa.String(length=255), nullable=False),
    sa.Column('administered_on', sa.Date(), nullable=False),
    sa.Column('next_due_on', sa.Date(), nullable=True),
    sa.Column('dosage', sa.String(length=100), nullable=True),
    sa.Column('administered_by', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_parasite_preventions_dog_id', 'parasite_preventions', ['dog_id'], unique=False)
    op.create_index('ix_parasite_preventions_product_name', 'parasite_preventions', ['product_name'], unique=False)
    op.create_index('ix_parasite_preventions_administered_on', 'parasite_preventions', ['administered_on'], unique=False)
    op.create_index('ix_parasite_preventions_next_due_on', 'parasite_preventions', ['next_due_on'], unique=False)


def downgrade() -> None:
    # Drop parasite_preventions table
    op.drop_index('ix_parasite_preventions_next_due_on', table_name='parasite_preventions')
    op.drop_index('ix_parasite_preventions_administered_on', table_name='parasite_preventions')
    op.drop_index('ix_parasite_preventions_product_name', table_name='parasite_preventions')
    op.drop_index('ix_parasite_preventions_dog_id', table_name='parasite_preventions')
    op.drop_table('parasite_preventions')