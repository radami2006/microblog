import sys
import os

# Add the application directory to the Python path
project_home = os.path.expanduser('~/microblog')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key'  # Change this to a secure value

# Define database path - important for PythonAnywhere
instance_path = os.path.join(project_home, 'instance')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(instance_path, 'app.db')

# Ensure instance directory exists
try:
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
except Exception as e:
    print(f"Error creating instance directory: {e}")

# Ensure uploads directory structure exists
try:
    uploads_path = os.path.join(project_home, 'app/static/uploads')
    avatars_path = os.path.join(uploads_path, 'avatars')
    covers_path = os.path.join(uploads_path, 'covers')
    
    for path in [uploads_path, avatars_path, covers_path]:
        if not os.path.exists(path):
            os.makedirs(path)
except Exception as e:
    print(f"Error creating upload directories: {e}")

# Import the Flask application
from run import app as application  # This is the Flask application object