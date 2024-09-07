from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
import logging

load_dotenv()  # Load environment variables from .env

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, template_folder='templates')

    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Determine environment and load the appropriate configuration
    config_type = os.getenv('FLASK_ENV', 'development')
    if config_type == 'production':
        app.config.from_object('config_prod.Config')
    else:
        app.config.from_object('config_local.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    app.logger.debug("CSRF protection initialized.")

    with app.app_context():
        from . import models
        from .routes import bp
        db.create_all()
        app.register_blueprint(bp)

    return app
