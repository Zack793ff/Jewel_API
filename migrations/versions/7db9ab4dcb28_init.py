from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '7db9ab4dcb28'
down_revision: Union[str, None] = '0eeb0474136a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Get the current connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Get the columns in the gem table
    columns = [col['name'] for col in inspector.get_columns('gem')]
    
    # Add seller_id column if it doesn't exist
    if 'seller_id' not in columns:
        op.add_column('gem', sa.Column('seller_id', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'gem', 'user', ['seller_id'], ['id'])

def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns('gem')]
    
    if 'seller_id' in columns:
        op.drop_constraint(None, 'gem', type_='foreignkey')
        op.drop_column('gem', 'seller_id')
