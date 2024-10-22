# Copyright (c) 2024 Jason Wicks
# All rights reserved.
#
# Copyright pending.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from alembic.config import Config
from alembic import command
import os

# Create a Flask application instance
app = Flask(__name__)

# Set the database URL from the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create Alembic config
alembic_cfg = Config("migrations backup current/versions/alembic.ini")

# Use application context to run the migration
with app.app_context():
    command.upgrade(alembic_cfg, 'head')
