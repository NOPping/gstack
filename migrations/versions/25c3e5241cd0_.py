"""empty message

Revision ID: 25c3e5241cd0
Revises: 76bb287a37d
Create Date: 2014-07-27 16:19:12.634404

"""

# revision identifiers, used by Alembic.
revision = '25c3e5241cd0'
down_revision = '76bb287a37d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('accesstoken',
        sa.Column(
            'id_token',
            sa.String(length=1000),
            nullable=True
        )
    )

    op.add_column('refreshtoken',
        sa.Column(
            'id_token',
            sa.String(length=1000),
            nullable=True
        )
    )

def downgrade():
    pass
