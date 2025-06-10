"""Add image and image_processing_task tables

Revision ID: 0003
Revises: 0002
Create Date: 2025-06-09 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create images table
    op.create_table('images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_path', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_small_path', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_medium_path', sa.String(length=500), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('exif_data', sa.JSON(), nullable=True),
        sa.Column('exif_latitude', sa.Float(), nullable=True),
        sa.Column('exif_longitude', sa.Float(), nullable=True),
        sa.Column('exif_altitude', sa.Float(), nullable=True),
        sa.Column('exif_datetime', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('predicted_latitude', sa.Float(), nullable=True),
        sa.Column('predicted_longitude', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('alternative_locations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    op.create_index(op.f('ix_images_user_id'), 'images', ['user_id'], unique=False)
    
    # Create image_processing_tasks table
    op.create_table('image_processing_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('current_step', sa.String(length=255), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_processing_tasks_id'), 'image_processing_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_image_processing_tasks_image_id'), 'image_processing_tasks', ['image_id'], unique=False)
    op.create_index(op.f('ix_image_processing_tasks_task_id'), 'image_processing_tasks', ['task_id'], unique=True)


def downgrade() -> None:
    # Drop image_processing_tasks table
    op.drop_index(op.f('ix_image_processing_tasks_task_id'), table_name='image_processing_tasks')
    op.drop_index(op.f('ix_image_processing_tasks_image_id'), table_name='image_processing_tasks')
    op.drop_index(op.f('ix_image_processing_tasks_id'), table_name='image_processing_tasks')
    op.drop_table('image_processing_tasks')
    
    # Drop images table
    op.drop_index(op.f('ix_images_user_id'), table_name='images')
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_table('images')