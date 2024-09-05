from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from config import Config
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import os
import logging


load_dotenv()

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

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    WTF_CSRF_ENABLED = True

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    app.logger.debug("CSRF protection initialized.")

    with app.app_context():
        from . import models
        from .routes import bp
        from .models import User
        db.create_all()
        app.register_blueprint(bp)

    return app
