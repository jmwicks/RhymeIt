import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
                              'postgresql://admin:iZz6y5nnvJjbNLTlvsmX0WgqiLKVKWkH@7tirbs.stackhero-network.com:6759/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv('SECRET_KEY') or 'mauGO9eK66xpitdLL7tRvp2x2v2LoGku'
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'a_default_salt')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY') or 'your_csrf_secret_key'
    WTF_CSRF_ENABLED = True

    DEBUG = False

    # Session settings
    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY = None
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=365 * 10)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'rhyme.it.manager@gmail.com')
