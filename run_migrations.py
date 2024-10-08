import os
from alembic.config import Config
from alembic import command

# Create an Alembic Config object and specify the path to alembic.ini
alembic_cfg = Config('migrations/alembic.ini')  # Adjust path if needed

# Set the sqlalchemy.url from the environment variable
alembic_cfg.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))

# Run the upgrade command to apply migrations
command.upgrade(alembic_cfg, 'head')
