"""add real butterfly data

Revision ID: b03a9e2e3c05
Revises: 264b99aa6b56
Create Date: 2022-02-16 19:26:49.775728

"""
from alembic import op
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from image import get_butterfly_names, IMAGE_URL_PREFIX, IMAGE_SUFFIX
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b03a9e2e3c05'
down_revision = '264b99aa6b56'
branch_labels = None
depends_on = None



def upgrade():
    butterfly_names = get_butterfly_names()
    values = [f"(1600, '{n}', '{IMAGE_URL_PREFIX}{n}{IMAGE_SUFFIX}')" for n in butterfly_names]
    values_string =','.join(values)
    sql_string = """INSERT INTO butterflies
        (rating, name, image_url)
        VALUES {values};""".format(values=values_string)
    op.execute(sql_string)


def downgrade():
    op.execute("""
    DELETE FROM butterflies WHERE image_url LIKE '%cloudfront_%';
    """)
