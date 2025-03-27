import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    
    # For PythonAnywhere, we need to handle the database path differently
    # This ensures the instance folder exists and is writable
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        try:
            os.makedirs(instance_path)
        except Exception as e:
            print(f"Warning: Could not create instance directory: {e}", file=sys.stderr)
    
    # Use DATABASE_URL environment variable if set, otherwise use a local SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
