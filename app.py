import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI", "")
    app.config["DATABASE_NAME"] = os.getenv("DATABASE_NAME", "auth_app")

    mongo_uri = app.config["MONGO_URI"]
    users = None
    if mongo_uri:
        client = MongoClient(mongo_uri)
        db = client[app.config["DATABASE_NAME"]]
        users = db.users
        users.create_index("email", unique=True)

    def login_required(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        return wrapped_view

    def get_users_collection():
        if users is None:
            flash(
                "MongoDB is not configured yet. Add your Atlas connection string to the .env file.",
                "warning",
            )
            return None
        return users

    @app.context_processor
    def inject_user():
        return {"current_user_name": session.get("user_name")}

    @app.get("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            users_collection = get_users_collection()
            if users_collection is None:
                return render_template("register.html")

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not all([name, email, password, confirm_password]):
                flash("Please fill in every field.", "danger")
                return render_template("register.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("register.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters long.", "danger")
                return render_template("register.html")

            user = {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash(password),
            }

            try:
                result = users_collection.insert_one(user)
            except DuplicateKeyError:
                flash("An account with that email already exists.", "danger")
                return render_template("register.html")

            session["user_id"] = str(result.inserted_id)
            session["user_name"] = name
            flash("Registration successful. Welcome aboard!", "success")
            return redirect(url_for("dashboard"))

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            users_collection = get_users_collection()
            if users_collection is None:
                return render_template("login.html")

            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("login.html")

            user = users_collection.find_one({"email": email})
            if not user or not check_password_hash(user["password_hash"], password):
                flash("Invalid email or password.", "danger")
                return render_template("login.html")

            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    @app.post("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
