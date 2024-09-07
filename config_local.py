import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://wicksjm:Ilvbbaicnl1!@localhost:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for CSRF protection and session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mauGO9eK66xpitdLL7tRvp2x2v2LoGku'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'a_default_salt')
    WTF_CSRF_ENABLED = True

    # Debug mode setting
    DEBUG = True
