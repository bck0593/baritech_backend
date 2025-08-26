"""simple vaccinations table

Revision ID: simple_vaccs
Revises: eaaa75531305
Create Date: 2025-08-26 07:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'simple_vaccs'
down_revision = 'eaaa75531305'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vaccinations table only
    op.create_table('vaccinations',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('dog_id', sa.String(length=255), nullable=False),
    sa.Column('vaccine_name', sa.String(length=255), nullable=False),
    sa.Column('administered_on', sa.Date(), nullable=False),
    sa.Column('next_due_on', sa.Date(), nullable=True),
    sa.Column('administered_by', sa.String(length=255), nullable=True),
    sa.Column('lot_number', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vaccinations_dog_id', 'vaccinations', ['dog_id'], unique=False)
    op.create_index('ix_vaccinations_vaccine_name', 'vaccinations', ['vaccine_name'], unique=False)
    op.create_index('ix_vaccinations_administered_on', 'vaccinations', ['administered_on'], unique=False)
    op.create_index('ix_vaccinations_next_due_on', 'vaccinations', ['next_due_on'], unique=False)


def downgrade() -> None:
    # Drop vaccinations table
    op.drop_index('ix_vaccinations_next_due_on', table_name='vaccinations')
    op.drop_index('ix_vaccinations_administered_on', table_name='vaccinations')
    op.drop_index('ix_vaccinations_vaccine_name', table_name='vaccinations')
    op.drop_index('ix_vaccinations_dog_id', table_name='vaccinations')
    op.drop_table('vaccinations')