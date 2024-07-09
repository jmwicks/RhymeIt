import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for CSRF protection and session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mauGO9eK66xpitdLL7tRvp2x2v2LoGku'

    # Debug mode setting
    DEBUG = True
