import bcrypt
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_passwords():
    """Fetch users, check passwords, and hash any plain-text passwords."""
    print("🔍 Fetching users from Supabase...")

    # Retrieve all users
    response = supabase.table("users").select("id, email, password").execute()

    if not response.data:
        print("✅ No users found or all passwords are already hashed.")
        return

    for user in response.data:
        user_id = user["id"]
        email = user["email"]
        plain_password = user["password"]

        # ✅ Skip if password is already hashed (bcrypt hash starts with "$2b$")
        if plain_password.startswith("$2b$"):
            print(f"🔹 {email} already has a hashed password. Skipping...")
            continue

        # 🔹 Hash plain-text password
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 🔹 Update Supabase with the hashed password
        supabase.table("users").update({"password": hashed_password}).eq("id", user_id).execute()
        print(f"✅ Hashed password for {email}")

    print("🚀 Password migration completed!")

if __name__ == "__main__":
    migrate_passwords()
