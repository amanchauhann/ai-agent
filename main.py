# main.py (updated for Supabase)

import os
from supabase import create_client, Client

# Import our agent classes and functions
from harvester import run_harvester
from agent2_cleaner import CleanerTaggerAgent
from agent3_summarizer import SummarizerAgent
# We don't need the personalizer for this script, as it runs in the API layer
# from agent4_personalizer import PersonalizationAgent, record_user_interaction

# --- SUPABASE CONFIGURATION ---
# Replace with your own Supabase URL and Key
SUPABASE_URL = "https://trjasylbjajerzbiwvxi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRyamFzeWxiamFqZXJ6Yml3dnhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4ODcxMDksImV4cCI6MjA2NzQ2MzEwOX0.Qf4xfr5-bGQJZJu43rmv1xRp68nM4i_PB5Lzz9o33HQ"

# Initialize the Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Successfully connected to Supabase.")
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    exit() # Exit if we can't connect

def run_pipeline():
    """
    Runs the AI news pipeline (Agents 1-3) and saves the results to Supabase.
    """

    # 1. Initialize Agents
    print("Initializing agents...")
    cleaner_agent = CleanerTaggerAgent()
    summarizer_agent = SummarizerAgent()
    print("-" * 30)

    # 2. AGENT 1: Harvest raw articles
    print("Starting Agent 1: Harvester...")
    raw_articles = run_harvester()
    if not raw_articles:
        print("Harvester found no articles. Exiting pipeline.")
        return
    print(f"Harvested {len(raw_articles)} articles.")
    print("-" * 30)

    # 3. AGENTS 2 & 3: Clean, Tag, and Summarize
    print("Starting Agents 2 & 3: Cleaner, Tagger, and Summarizer...")
    articles_to_upload = []
    for article in raw_articles:
        print(f"Processing: {article['headline']}")
        # Agent 2
        cleaned_article = cleaner_agent.process_article(article)
        # Agent 3
        final_article = summarizer_agent.summarize_article(cleaned_article)
        
        # Prepare the data for Supabase, ensuring it matches our table columns
        # The 'entities' field is a dictionary, which will be saved as JSONB
        db_record = {
            'headline': final_article.get('headline'),
            'url': final_article.get('url'),
            'summary': final_article.get('summary'),
            'category': final_article.get('category'),
            'entities': final_article.get('entities'),
            'content': final_article.get('content')
        }
        articles_to_upload.append(db_record)

    print("Finished processing all articles.")
    print("-" * 30)

    # 4. Store the final result in Supabase
    print(f"Uploading {len(articles_to_upload)} articles to Supabase...")
    if articles_to_upload:
        try:
            # 'upsert' will insert new articles or update existing ones if the URL matches.
            # This is perfect for preventing duplicate articles.
            data, count = supabase.table('articles').upsert(articles_to_upload, on_conflict='url').execute()
            print(f"Successfully uploaded/updated articles in Supabase.")
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    run_pipeline()
    print("\n--- AI News Pipeline has completed its run. ---")