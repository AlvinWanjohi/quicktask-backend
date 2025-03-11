import jwt
import datetime
import logging
from flask import current_app


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_token(user_id):
    """
    Generate a JWT token for authentication.
    """
    try:
        payload = {
            "user_id": user_id,
            "iat": datetime.datetime.utcnow(), 
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30) 
        }
        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return token
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        return None

def verify_token(token):
    """
    Verify and decode the JWT token.
    Supports tokens with 'Bearer' prefix.
    """
    try:
        if token.startswith("Bearer "): 
            token = token.split(" ")[1]

        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return {"valid": True, "user_id": payload.get("user_id")}

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return {"valid": False, "error": "Token expired"}

    except jwt.DecodeError:
        logger.warning("JWT decode error - Invalid token format")
        return {"valid": False, "error": "Invalid token format"}

    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return {"valid": False, "error": "Invalid token"}

    except Exception as e:
        logger.error(f"Unexpected JWT error: {e}")
        return {"valid": False, "error": "Token verification failed"}
