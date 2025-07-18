"""Add role to User model

Revision ID: 294155af5f9b
Revises: 6454dc185f15
Create Date: 2025-06-29 15:02:51.955413

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "294155af5f9b"
down_revision = "6454dc185f15"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("role")

    # ### end Alembic commands ###
