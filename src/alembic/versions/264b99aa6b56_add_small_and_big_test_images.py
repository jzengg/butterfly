"""add small and big test images

Revision ID: 264b99aa6b56
Revises: 67240db5095a
Create Date: 2022-02-15 23:54:52.880508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '264b99aa6b56'
down_revision = '67240db5095a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    INSERT INTO butterflies
  (rating, name, image_url)
VALUES
  (1600, 'test_big', 'https://hotbutterfly.s3.amazonaws.com/big.jpeg'),
  (1600, 'test_small', 'https://hotbutterfly.s3.amazonaws.com/small.jpeg')
    """)


def downgrade():
    op.execute("""
    DELETE FROM butterflies WHERE name LIKE 'test_%';
    """)
