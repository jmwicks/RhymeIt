import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
                              'postgresql://admin:iZz6y5nnvJjbNLTlvsmX0WgqiLKVKWkH@7tirbs.stackhero-network.com:6759/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mauGO9eK66xpitdLL7tRvp2x2v2LoGku'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'a_default_salt')
    WTF_CSRF_ENABLED = True

    DEBUG = True
