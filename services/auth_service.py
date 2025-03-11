from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from utils.validators import validate_email, validate_password
from models.user import User
from utils.database import db

def register_user():
    """Registers a new user with validation and error handling."""
    try:
        print("\n[DEBUG] Register User Request")
        print("Headers:", request.headers)
        print("Raw Data:", request.data)

        if not request.is_json:
            return jsonify({"error": "Missing or incorrect Content-Type. Expected 'application/json'"}), 400

        data = request.get_json()
        print("Parsed JSON:", data)

        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([username, email, password]):
            return jsonify({"error": "All fields (username, email, password) are required"}), 400

        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({"error": password_message}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email is already registered"}), 409

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Database error: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

def login_user():
    """Logs in an existing user and returns an access token."""
    try:
        print("\n[DEBUG] Login User Request")
        print("Headers:", request.headers)
        print("Raw Data:", request.data)

        if not request.is_json:
            return jsonify({"error": "Missing or incorrect Content-Type. Expected 'application/json'"}), 400

        data = request.get_json()
        print("Parsed JSON:", data)

        if not data:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=user.id)

        return jsonify({
            "message": "Login successful",
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 200

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
