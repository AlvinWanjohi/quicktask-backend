import re

def validate_email(email):
    """Checks if the email format is valid."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(email_regex, email))

def validate_password(password):
    """Checks if the password meets security requirements."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one number.")
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")

    if errors:
        return False, errors 
    return True, "Password is valid."
