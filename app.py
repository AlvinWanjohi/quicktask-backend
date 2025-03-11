import os
import logging
import bcrypt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from flask_migrate import Migrate
from supabase import create_client, Client
from config import Config
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

supabase: Optional[Client] = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS (Allow frontend origin & credentials)
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    # Initialize database, migrations, and JWT
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or API Key is missing. Set them in the .env file.")
        raise ValueError("Supabase URL or API Key is missing. Set them in the .env file.")

    global supabase
    supabase = create_client(supabase_url, supabase_key)
    logger.info("Supabase initialized successfully.")

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.task_routes import task_bp
    from routes.bid_routes import bid_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(task_bp, url_prefix="/tasks")
    app.register_blueprint(bid_bp, url_prefix="/bids")

    return app

app = create_app()

# -------------------  USER REGISTRATION -------------------

@app.route("/register", methods=["POST"])
def register():
    """User registration - Stores user info in Supabase and returns a token."""
    data = request.get_json()

    # Extract user details
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing fields", "success": False}), 400

    try:
        # Check if user already exists
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"error": "User already exists", "success": False}), 400

        # Hash password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create user in Supabase Auth
        response = supabase.auth.sign_up({"email": email, "password": password})

        if hasattr(response, "error") and response.error:
            return jsonify({"error": response.error.message, "success": False}), 400

        user_id = response.user.id if response.user else None

        # Insert user data into 'users' table
        user_data = {
            "id": user_id,  # Unique ID from Supabase Auth
            "name": name,
            "email": email,
            "password": hashed_password  # Store securely hashed password
        }
        supabase.table("users").insert(user_data).execute()

        # Generate JWT token
        access_token = create_access_token(identity=user_id)  # Use user ID for security
        return jsonify({"access_token": access_token, "success": True}), 201

    except Exception as e:
        logger.exception("Error during user registration")
        return jsonify({"error": "An error occurred while registering", "details": str(e), "success": False}), 500

# -------------------  USER LOGIN -------------------

@app.route("/login", methods=["POST"])
def login():
    """User login - Checks email & password, returns JWT."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password", "success": False}), 400

    try:
        # Retrieve user data from Supabase
        response = supabase.table("users").select("id, email, password").eq("email", email).execute()

        if not response.data:
            return jsonify({"error": "User not found", "success": False}), 404

        user = response.data[0]

        # Ensure password is securely stored
        stored_password = user["password"]
        if not stored_password.startswith("$2b$"):
            return jsonify({
                "error": "Password not securely stored. Please reset your password.",
                "success": False
            }), 400

        # Check if the hashed password matches
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return jsonify({"error": "Incorrect password", "success": False}), 401

        # Generate JWT token
        access_token = create_access_token(identity=user["id"])
        return jsonify({"access_token": access_token, "success": True}), 200

    except Exception as e:
        logger.exception("Error during login")
        return jsonify({"error": "An error occurred while logging in", "details": str(e), "success": False}), 500

# ------------------- SECURED ROUTES -------------------

@app.route('/tasks', methods=['GET'])
@jwt_required()  # Protect route with JWT authentication
def get_tasks():
    """Retrieve tasks from Supabase (Requires JWT)."""
    try:
        current_user_id = get_jwt_identity()  # Get authenticated user
        logger.info(f"Fetching tasks for user ID: {current_user_id}")

        response = supabase.table('tasks').select('*').execute()

        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error.message}")
            return jsonify({"error": response.error.message}), 500

        tasks = getattr(response, 'data', None)
        if tasks is None:
            return jsonify({"error": "No tasks found"}), 404

        return jsonify(tasks)

    except Exception as e:
        logger.exception("Error fetching tasks")
        return jsonify({"error": "An error occurred while fetching tasks", "details": str(e)}), 500

@app.route('/tasks/<int:task_id>/bids', methods=['GET'])
@jwt_required()  # Protect route with JWT authentication
def get_bids(task_id):
    """Retrieve bids for a specific task from Supabase (Requires JWT)."""
    try:
        current_user_id = get_jwt_identity()  # Get authenticated user
        logger.info(f"Fetching bids for task {task_id} by user ID {current_user_id}")

        response = supabase.table('bids').select('*').eq('task_id', task_id).execute()

        if hasattr(response, 'error') and response.error:
            logger.error(f"Supabase error: {response.error.message}")
            return jsonify({"error": response.error.message}), 500

        bids = getattr(response, 'data', None)
        if bids is None:
            return jsonify({"error": "No bids found for this task"}), 404

        return jsonify(bids)

    except Exception as e:
        logger.exception(f"Error fetching bids for task {task_id}")
        return jsonify({"error": "An error occurred while fetching bids", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
