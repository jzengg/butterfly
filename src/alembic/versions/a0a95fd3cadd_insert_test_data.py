"""insert test data

Revision ID: a0a95fd3cadd
Revises: 1070016eedc1
Create Date: 2022-01-15 21:09:25.338427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0a95fd3cadd'
down_revision = '1070016eedc1'
branch_labels = None
depends_on = None



def upgrade():
    op.execute("""
    INSERT INTO butterflies
  (rating, name, image_url)
VALUES
  (1600, 'test_allison', 'http://media.oregonlive.com/hg_impact/photo/11221031-large.jpg'),
  (1600, 'test_jimmy', 'http://media.oregonlive.com/hg_impact/photo/11221048-large.jpg'),
  (1600, 'test_jeffrey', 'http://media.oregonlive.com/hg_impact/photo/11221042-large.jpg'),
  (1600, 'test_yang', 'http://media.oregonlive.com/hg_impact/photo/11221062-large.jpg');
    """)


def downgrade():
    op.execute("""
    DELETE FROM butterflies WHERE name LIKE 'test_%';
    """)
