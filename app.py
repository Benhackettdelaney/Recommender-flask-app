from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from flask_migrate import Migrate

# My app
app = Flask(__name__)
Scss(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recommender.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "your_secret_key_here"  # Replace with a strong secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# A helper function to check if the user is authenticated
def current_user_is_authenticated():
    try:
        get_jwt_identity()  # This will raise an error if the user is not authenticated
        return True
    except:
        return False

# Before request to check if the user is authenticated
@app.before_request
def before_request():
    if not current_user_is_authenticated() and request.endpoint not in ['login', 'register']:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Data class, row of data
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Movie {self.id}"

# User model for login and registration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.username}"

# HomePage
@app.route('/', methods=["POST", "GET"])
@jwt_required(optional=True)  # This makes the route accessible for logged-in and non-logged-in users
def index():
    if request.method == "POST":
        current_movie = request.form["content"]
        new_movie = Movie(content=current_movie)
        try:
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"

    else:
        movies = Movie.query.order_by(Movie.created).all()
        return render_template("index.html", movies=movies)

# Edit movie
@app.route("/update/<int:id>", methods=["GET", "POST"])
@jwt_required()  # Protected route; only accessible with a valid JWT token
def update(id: int):
    movie = Movie.query.get_or_404(id)
    if request.method == "POST":
        movie.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR: {e}")
            return f"ERROR: {e}"

    return render_template("update.html", movie=movie)

# Delete movie
@app.route("/delete/<int:id>", methods=["GET"])
@jwt_required()  # Protected route
def delete(id: int):
    delete_movie = Movie.query.get_or_404(id)
    try:
        db.session.delete(delete_movie)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR: {e}"

# Register route (create a new user)
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            message = "Username already exists"
            return render_template("register.html", message=message)

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))  # Redirect to login after successful registration

    return render_template("register.html")

# Login route (authenticate user and return a JWT token)
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Create JWT token
            access_token = create_access_token(identity=user.id, fresh=True)
            return redirect(url_for('index'))  # Redirect to home page after successful login

        message = "Invalid credentials"
        return render_template("login.html", message=message)

    return render_template("login.html")

# Protected route (requires valid token)
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()  # Get the user ID from the JWT
    user = User.query.get(current_user_id)
    return jsonify(logged_in_as=user.username), 200

# Logout route (remove token) - Not implemented fully, JWT tokens are stateless
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Token removal isn't needed as JWT is stateless; you'd need a token blacklist for that
    return jsonify({"message": "Successfully logged out"}), 200

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
