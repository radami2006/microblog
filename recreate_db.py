import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Remove existing database file if it exists
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    except Exception as e:
        print(f"Error removing database: {e}")

# Now create the new database with our updated schema
from app import create_app, db
from app.models import User, Post

def recreate_database():
    app = create_app()
    with app.app_context():
        print("Creating new database with updated schema...")
        db.create_all()
        print("Database schema created successfully!")
        
        # Create a test user if database is empty
        if not User.query.first():
            test_user = User(username="testuser", email="test@example.com")
            test_user.set_password("test123")
            db.session.add(test_user)
            db.session.commit()
            print("Created test user: username=testuser, password=test123")

if __name__ == '__main__':
    recreate_database()