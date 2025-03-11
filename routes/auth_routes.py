from flask import Blueprint, request, jsonify, make_response
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/check-auth-status", methods=["GET"])
def check_auth_status():
    """Check if user has registered before or is logged in"""
    # Check for existing session token or stored credentials
    has_account = request.cookies.get('has_registered')
    is_logged_in = request.cookies.get('auth_token')
    
    if is_logged_in:
        return jsonify({"status": "authenticated", "redirect": "dashboard"})
    elif has_account:
        return jsonify({"status": "has_account", "redirect": "login"})
    else:
        return jsonify({"status": "new_user", "redirect": "register"})

@auth_bp.route("/register", methods=["POST"])
def register():
    """Handles user registration."""
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid Content-Type. Expected 'application/json'"}), 400

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["email", "password", "name"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Get registration result from service
        result = register_user(data)
        
        # Check if the result is a tuple containing response and status code
        if isinstance(result, tuple) and len(result) == 2:
            response_data, status_code = result
        else:
            # If not, assume it's just the response data with default 200 status
            response_data, status_code = result, 200
        
        # If registration is successful (status code 200 or 201)
        if status_code in (200, 201):
            # Create a response object from the result
            if isinstance(response_data, dict):
                response = make_response(jsonify(response_data), status_code)
            else:
                response = make_response(response_data, status_code)
                
            # Set a cookie to remember the user has registered
            response.set_cookie('has_registered', 'true', max_age=31536000)  # 1 year
            return response
        
        # If not successful, return the original result
        if isinstance(response_data, dict):
            return jsonify(response_data), status_code
        return response_data, status_code

    except Exception as e:
        return jsonify({"error": "An error occurred during registration", "details": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Handles user login."""
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid Content-Type. Expected 'application/json'"}), 400

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["email", "password"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Get login result from service
        result = login_user(data)
        
        # Check if the result is a tuple containing response and status code
        if isinstance(result, tuple) and len(result) == 2:
            response_data, status_code = result
        else:
            # If not, assume it's just the response data with default 200 status
            response_data, status_code = result, 200
        
        # If login is successful and returns a token
        if status_code == 200 and isinstance(response_data, dict) and "token" in response_data:
            response = make_response(jsonify(response_data), status_code)
            # Set auth token cookie - adjust max_age according to your token expiration
            response.set_cookie('auth_token', response_data["token"], max_age=86400, httponly=True)  # 24 hours
            return response
        
        # If not successful, return the original result
        if isinstance(response_data, dict):
            return jsonify(response_data), status_code
        return response_data, status_code

    except Exception as e:
        return jsonify({"error": "An error occurred during login", "details": str(e)}), 500

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Handles user logout."""
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.delete_cookie('auth_token')
    return response