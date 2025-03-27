from app import create_app, db
from app.models import User, Post

def update_database():
    app = create_app()
    with app.app_context():
        print("Updating database schema...")
        db.create_all()
        print("Database schema updated successfully.")

if __name__ == '__main__':
    update_database()