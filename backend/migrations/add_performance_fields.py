"""
Database migration to add performance optimization fields
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Add performance optimization fields to analyses table"""
    
    # Add new columns to analyses table
    op.add_column('analyses', sa.Column('status_message', sa.String(200), nullable=True))
    op.add_column('analyses', sa.Column('processing_time_seconds', sa.Float, nullable=True))
    op.add_column('analyses', sa.Column('concurrent_processing_used', sa.Boolean, default=False))
    op.add_column('analyses', sa.Column('cache_hit_rate', sa.Float, nullable=True))
    
    # Add indexes for performance
    op.create_index('idx_analyses_status', 'analyses', ['status'])
    op.create_index('idx_analyses_created_at', 'analyses', ['created_at'])
    op.create_index('idx_analyses_user_status', 'analyses', ['user_id', 'status'])
    
    # Add indexes to brands table for faster lookups
    op.create_index('idx_brands_name', 'brands', ['name'])
    
    # Add indexes to users table
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])


def downgrade():
    """Remove performance optimization fields"""
    
    # Drop indexes
    op.drop_index('idx_analyses_status', 'analyses')
    op.drop_index('idx_analyses_created_at', 'analyses')
    op.drop_index('idx_analyses_user_status', 'analyses')
    op.drop_index('idx_brands_name', 'brands')
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_created_at', 'users')
    
    # Drop columns
    op.drop_column('analyses', 'status_message')
    op.drop_column('analyses', 'processing_time_seconds')
    op.drop_column('analyses', 'concurrent_processing_used')
    op.drop_column('analyses', 'cache_hit_rate')
