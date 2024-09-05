from app import db  # Import the db instance from your __init__.py
from sqlalchemy.exc import SQLAlchemyError
from app.models import User


# Define the user model using Flask-SQLAlchemy

# Function to add a new user
def register_user(username, password_hash, email):
    try:
        new_user = User(username=username, password_hash=password_hash, email=email)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} registered successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error registering user: {e}")

# Example usage of register_user function
#register_user('test_user1', 'hashed_password', 'test@test.com')
