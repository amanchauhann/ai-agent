# /api/cron.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
import os

# IMPORTANT: Make sure your agent files are in the root directory
# so they can be imported correctly.
from harvester import run_harvester
from agent2_cleaner import CleanerTaggerAgent
from agent3_summarizer import SummarizerAgent
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- PIPELINE LOGIC ---
def run_full_pipeline():
    """
    The complete pipeline logic from main.py, refactored into a function.
    """
    print("--- PIPELINE STARTED ---")
    # Initialize Supabase client inside the function
    # This is crucial for serverless environments.
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    cleaner_agent = CleanerTaggerAgent()
    summarizer_agent = SummarizerAgent()

    raw_articles = run_harvester()
    if not raw_articles:
        print("Harvester found no articles.")
        return

    articles_to_upload = []
    for article in raw_articles:
        cleaned_article = cleaner_agent.process_article(article)
        final_article = summarizer_agent.summarize_article(cleaned_article)
        db_record = { 'headline': final_article.get('headline'), 'url': final_article.get('url'), 'summary': final_article.get('summary'), 'category': final_article.get('category'), 'entities': final_article.get('entities'), 'content': final_article.get('content') }
        articles_to_upload.append(db_record)

    if articles_to_upload:
        supabase.table('articles').upsert(articles_to_upload, on_conflict='url').execute()
        print(f"--- PIPELINE COMPLETE: Uploaded {len(articles_to_upload)} articles. ---")

# --- API ENDPOINT FOR THE CRON JOB ---
@app.post("/cron")
def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    This endpoint is called by the cron scheduler.
    It adds the long-running pipeline task to the background.
    """
    # We add the task to the background to immediately return a response
    # to the cron scheduler, preventing a timeout on their end.
    background_tasks.add_task(run_full_pipeline)
    return {"message": "Pipeline started successfully in the background."}