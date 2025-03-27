from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler
import os
from sqlalchemy import inspect

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)

    # Ensure database tables exist
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            app.logger.warning("Database tables not found. Creating tables...")
            try:
                db.create_all()
                app.logger.info("Database tables created successfully.")
            except Exception as e:
                app.logger.error(f"Failed to create database tables: {str(e)}")

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp)
    
    # Set up logging for production
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # Set up file handler for app.log
        file_handler = RotatingFileHandler('logs/microblog.log', 
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        
        # Add handlers and set log level
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app
