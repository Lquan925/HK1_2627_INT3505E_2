from alembic import context

from product_api import create_app
from product_api.extensions import db
from product_api import models

app = create_app()

with app.app_context():
    if context.is_offline_mode():
        context.configure(url=app.config["SQLALCHEMY_DATABASE_URI"], target_metadata=db.metadata, literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()
    else:
        with db.engine.connect() as connection:
            context.configure(connection=connection, target_metadata=db.metadata, render_as_batch=True)
            with context.begin_transaction():
                context.run_migrations()
