# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from website.restAPI import api_bp

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
socketio = SocketIO()  # Initialize SocketIO

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    
    # Configure SocketIO with the app
    socketio.init_app(app)

    app.register_blueprint(api_bp)

    # Configuration settings
    app.config['SECRET_KEY'] = 'for testing'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'infogenesis.communications@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vmnr srlx wsar tyjd'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    
    # Initialize extensions with the app
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    with app.app_context():
        try:
            # Attempt to create all tables
            db.create_all()
            print("Database created and initialized successfully.")
        except Exception as e:
            print(f"Error during database initialization: {e}")

    # Load user function for login manager
    @login_manager.user_loader
    def load_user(id):
        from .models import User  # Import inside function to avoid circular import
        return User.query.get(int(id))

    return app





