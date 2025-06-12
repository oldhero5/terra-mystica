"""Add S3 fields to images table

Revision ID: 003
Revises: 002
Create Date: 2024-12-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add S3-related columns to images table
    op.add_column('images', sa.Column('s3_key', sa.String(500), nullable=True))
    op.add_column('images', sa.Column('s3_url', sa.String(1000), nullable=True))
    op.add_column('images', sa.Column('thumbnail_small_url', sa.String(1000), nullable=True))
    op.add_column('images', sa.Column('thumbnail_medium_url', sa.String(1000), nullable=True))
    op.add_column('images', sa.Column('thumbnail_large_url', sa.String(1000), nullable=True))
    
    # Create index on s3_key for faster lookups
    op.create_index('ix_images_s3_key', 'images', ['s3_key'])


def downgrade():
    # Remove index
    op.drop_index('ix_images_s3_key', 'images')
    
    # Remove S3-related columns
    op.drop_column('images', 'thumbnail_large_url')
    op.drop_column('images', 'thumbnail_medium_url')
    op.drop_column('images', 'thumbnail_small_url')
    op.drop_column('images', 's3_url')
    op.drop_column('images', 's3_key')