# routes/movie_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Movie

# Define the Blueprint
movies_bp = Blueprint('movies', __name__)

# Home page route
@movies_bp.route("/", methods=["POST", "GET"])
@jwt_required(optional=True)
def index():
    current_user = get_jwt_identity()  # Will be None if not logged in
    if request.method == "POST" and current_user:
        current_movie = request.form["content"]
        if not current_movie:
            return render_template("index.html", message="Movie content cannot be empty")

        new_movie = Movie(content=current_movie)
        try:
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            app.logger.error(f"Error occurred: {e}")
            return render_template("error.html", message="An unexpected error occurred.")

    movies = Movie.query.order_by(Movie.created).all()
    return render_template("index.html", movies=movies, current_user=current_user)

# Update movie route
@movies_bp.route("/update/<int:id>", methods=["GET", "POST"])
@jwt_required()
def update(id):
    movie = Movie.query.get_or_404(id)
    current_user = get_jwt_identity()
    if movie.user_id != current_user:
        return jsonify({"message": "You are not authorized to update this movie."}), 403

    if request.method == "POST":
        content = request.form["content"]
        if not content:
            return render_template("update.html", movie=movie, message="Content cannot be empty")
        movie.content = content
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            app.logger.error(f"Error occurred: {e}")
            return render_template("error.html", message="An unexpected error occurred.")

    return render_template("update.html", movie=movie)

# Delete movie route
@movies_bp.route("/delete/<int:id>", methods=["GET"])
@jwt_required()
def delete(id):
    movie = Movie.query.get_or_404(id)
    current_user = get_jwt_identity()
    if movie.user_id != current_user:
        return jsonify({"message": "You are not authorized to delete this movie."}), 403
    
    try:
        db.session.delete(movie)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return render_template("error.html", message="An unexpected error occurred.")
