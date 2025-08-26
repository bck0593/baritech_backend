"""priority_e certificates

Revision ID: 017_create_certificates_table
Revises: simple_parasite
Create Date: 2025-08-26 08:07:07.276131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '017_create_certificates_table'
down_revision = 'simple_parasite'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create certificates table
    op.create_table('certificates',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('dog_id', sa.String(length=255), nullable=False),
        sa.Column('cert_type', sa.Enum('狂犬病', '鑑札', '保険', '訓練', 'その他', name='certificatetype'), nullable=False),
        sa.Column('cert_number', sa.String(length=100), nullable=True),
        sa.Column('issuer', sa.String(length=255), nullable=False),
        sa.Column('issued_on', sa.Date(), nullable=False),
        sa.Column('expires_on', sa.Date(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_certificates_cert_type', 'certificates', ['cert_type'], unique=False)
    op.create_index(op.f('ix_certificates_dog_id'), 'certificates', ['dog_id'], unique=False)
    op.create_index('ix_certificates_expires_on', 'certificates', ['expires_on'], unique=False)
    op.create_index('ix_certificates_issued_on', 'certificates', ['issued_on'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_certificates_issued_on', table_name='certificates')
    op.drop_index('ix_certificates_expires_on', table_name='certificates')
    op.drop_index(op.f('ix_certificates_dog_id'), table_name='certificates')
    op.drop_index('ix_certificates_cert_type', table_name='certificates')
    
    # Drop table
    op.drop_table('certificates')