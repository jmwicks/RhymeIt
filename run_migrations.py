from flask import Flask
from flask_migrate import Migrate
from alembic.config import Config
from alembic import command
import os

# Create a Flask application instance
app = Flask(__name__)

# Configure your app here (e.g., app.config.from_object('config'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Initialize Flask-Migrate
migrate = Migrate(app)

# Create Alembic config
alembic_cfg = Config("migrations/alembic.ini")

# Use application context to run the migration
with app.app_context():
    command.upgrade(alembic_cfg, 'head')
