# get_token.py

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
# --- CONFIGURATION ---
# Use the same credentials as your api.py
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# The email and password of the test user you created in the Supabase UI
TEST_USER_EMAIL = "phantomthread.d@gmail.com"
TEST_USER_PASSWORD = "Rewari@123401"

# --- SCRIPT LOGIC ---
def get_jwt():
    """Signs in a user and prints their access token."""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connecting to Supabase to get token...")

        # Sign in the user
        response = supabase.auth.sign_in_with_password({
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })

        # Extract the access token (JWT) from the session
        access_token = response.session.access_token

        print("\n--- SUCCESS! ---")
        print("Your JWT access token is:\n")
        print(access_token)
        print("\nCopy this token (without quotes) and use it in the API docs.")

    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"Failed to get token: {e}")

if __name__ == "__main__":
    get_jwt()