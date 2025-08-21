# api.py (Updated with security scheme for docs)
# jus checking

from fastapi import FastAPI, Depends, HTTPException
# Import the new security classes
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from typing import Optional
import os
# Import our personalization agent
from agent4_personalizer import PersonalizationAgent
from dotenv import load_dotenv

load_dotenv()

# --- INITIALIZATION ---

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize the Personalization Agent
personalization_agent = PersonalizationAgent()

# Create an instance of the HTTPBearer security scheme
security = HTTPBearer()


# --- AUTHENTICATION DEPENDENCY (UPDATED) ---

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current user. It now depends on the HTTPBearer scheme.
    `credentials.credentials` will contain the token.
    """
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "AI News App API is running!"}


@app.get("/feed")
async def get_personalized_feed(current_user: dict = Depends(get_current_user)):
    # This endpoint's logic remains exactly the same
    user_id = current_user.id
    
    try:
        profile_response = supabase.table('user_profiles').select("interest_profile").eq('id', user_id).single().execute()
        user_profile_data = profile_response.data
        user_profile = {
            "categories": user_profile_data.get('interest_profile', {}).get('categories', {}),
            "entities": user_profile_data.get('interest_profile', {}).get('entities', {})
        }
    except Exception as e:
        user_profile = {"categories": {}, "entities": {}}

    try:
        articles_response = supabase.table('articles').select("*").order('created_at', desc=True).limit(50).execute()
        articles = articles_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {e}")

    ranked_articles = personalization_agent.rank_articles_for_user(user_profile, articles)

    return {"feed": ranked_articles}