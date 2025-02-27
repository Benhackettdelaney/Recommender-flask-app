from flask_sqlalchemy import SQLAlchemy

# initializing the database
db = SQLAlchemy()

# importing models
from .movie import Movie
from .user import User
