"""Create products table."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("qty_in_stock", sa.Integer(), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price_cents >= 0", name="price_nonnegative"),
        sa.CheckConstraint("qty_in_stock >= 0", name="stock_nonnegative"),
        sa.CheckConstraint("length(sku) BETWEEN 3 AND 32", name="sku_length"),
        sa.CheckConstraint("length(name) BETWEEN 1 AND 255", name="name_length"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_archived", "products", ["archived"])


def downgrade():
    op.drop_table("products")
