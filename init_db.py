from app import app, db
from app.models import User  # Import all models that need to be created

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_tables()

