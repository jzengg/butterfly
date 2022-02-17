"""remove test data

Revision ID: c0693a1b5f93
Revises: b03a9e2e3c05
Create Date: 2022-02-17 00:59:05.947359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0693a1b5f93'
down_revision = 'b03a9e2e3c05'
branch_labels = None
depends_on = None


def upgrade():
      op.execute("""
    DELETE FROM butterflies WHERE name LIKE 'test_%';
    """)


def downgrade():
        op.execute("""
    INSERT INTO butterflies
  (rating, name, image_url)
VALUES
  (1600, 'test_allison', 'http://media.oregonlive.com/hg_impact/photo/11221031-large.jpg'),
  (1600, 'test_jimmy', 'http://media.oregonlive.com/hg_impact/photo/11221048-large.jpg'),
  (1600, 'test_jeffrey', 'http://media.oregonlive.com/hg_impact/photo/11221042-large.jpg'),
  (1600, 'test_yang', 'http://media.oregonlive.com/hg_impact/photo/11221062-large.jpg');
    """)
