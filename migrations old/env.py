from __future__ import annotations
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy.ext.declarative import DeclarativeMeta

from app import db  # Import your db object

# Configuration object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db.metadata  # Set target metadata to your models metadata

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # Optional: ensure type changes are detected
        )

        with context.begin_transaction():
            context.run_migrations()

if __name__ == "__main__":
    run_migrations_online()
