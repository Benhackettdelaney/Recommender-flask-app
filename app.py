# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import DevelopmentConfig  # or ProductionConfig depending on the environment
from models import db  # Initialize db from the models module
from routes.auth import auth_bp  # Import auth blueprint directly
from routes.movie_routes import movies_bp  # Import movies blueprint directly



# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Load configuration settings

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Register blueprints for modular routes
app.register_blueprint(auth_bp, url_prefix="/auth")  # For authentication-related routes
app.register_blueprint(movies_bp, url_prefix="/movies")  # For movie-related routes

# Run the app
if __name__ == "__main__":
    app.run(debug=True)  # You can set debug=False for production
