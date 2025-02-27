# auth.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models import db, User
from flask_bcrypt import Bcrypt

# Initialize Bcrypt (after app context setup)
bcrypt = Bcrypt()

# Define the Blueprint
auth_bp = Blueprint('auth', __name__)

# Register route
@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return render_template("register.html", message="Username already exists")

        if len(password) < 8:
            return render_template("register.html", message="Password must be at least 8 characters")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# Login route
@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id, fresh=True)
            return redirect(url_for('movies.index'))

        return render_template("login.html", message="Invalid credentials")

    return render_template("login.html")


# Logout route (JWT is stateless, token revocation needs a blacklist implementation)
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Successfully logged out"}), 200


# Protected route (only accessible with a valid token)
@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200
