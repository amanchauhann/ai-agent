# harvester.py

import requests
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
# --- CONFIGURATION ---
# Replace 'YOUR_API_KEY' with the key you got from NewsAPI.org
API_KEY = os.environ.get("NEWS_API_KEY") 
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Define the parameters for our news search
# We're looking for top headlines in India in the technology category
params = {
    'q': 'Crypto',
    'apiKey': API_KEY
}

# --- AGENT LOGIC ---
def fetch_news_from_api():
    """Fetches a list of news articles from the NewsAPI."""
    print("Fetching news from NewsAPI...")
    
    # This is where we'll store the articles we find
    articles_found = []

    try:
        # Make the request to the API
        response = requests.get(NEWS_API_URL, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the list of articles
            articles = data.get('articles', [])
            
            print(f"Found {len(articles)} articles from the API.")

            # Process each article to get just the info we need
            for article in articles:
                articles_found.append({
                    'source': article['source']['name'],
                    'headline': article['title'],
                    'url': article['url']
                })
        else:
            print(f"Error fetching from API: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

    return articles_found

# --- MAIN EXECUTION ---
# if __name__ == "__main__":
#     api_articles = fetch_news_from_api()
    
#     # Print the results nicely
#     if api_articles:
#         print("\n--- Articles Fetched ---")
#         for i, article in enumerate(api_articles, 1):
#             print(f"{i}. {article['headline']} ({article['source']})")
#             print(f"   URL: {article['url']}\n")



            # --- NEW SCRAPING FUNCTION ---
def scrape_news_from_website():
    """Scrapes news headlines from a specific website."""
    # We will use The Hindu's tech section as an example
    # NOTE: Website structures change! This selector might need updating.
    SCRAPE_URL = 'https://www.thehindu.com/sci-tech/technology/'
    print(f"\nScraping news from {SCRAPE_URL}...")
    
    articles_found = []
    
    try:
        # We need headers to mimic a real browser
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(SCRAPE_URL, headers=headers)
        
        if response.status_code == 200:
            # Parse the page content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all headline elements. This is the part that needs inspection.
            # For The Hindu's tech section (as of late 2025), headlines are in <h2> tags
            # within a div that has a class containing 'story-card-news'.
            headlines = soup.select('h3.title a')

            print(f"Found {len(headlines)} articles from scraping.")
            
            for headline in headlines:
                articles_found.append({
                    'source': 'The Hindu (Scraped)',
                    'headline': headline.get_text(strip=True),
                    'url': headline['href']
                })
        else:
            print(f"Error scraping website: Status Code {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        
    return articles_found

# harvester.py (add this function)

def fetch_full_article_text(url):
    """
    Visits an article URL and scrapes the full text content.
    This is a generic scraper and might need to be customized for specific sites.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10) # Added a timeout

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # --- This is the part that needs customization ---
            # Try to find the main content in common tags like <article>, or divs with
            # class names like 'content', 'main-content', 'article-body'.
            # We'll look for a div that contains the most <p> tags.
            
            potential_containers = soup.find_all('div')
            main_content_container = None
            max_p_tags = 0

            for container in potential_containers:
                p_tags_count = len(container.find_all('p', recursive=False))
                if p_tags_count > max_p_tags:
                    max_p_tags = p_tags_count
                    main_content_container = container
            
            if main_content_container:
                # Join the text from all <p> tags within the best container
                paragraphs = main_content_container.find_all('p')
                full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
                return full_text
            else:
                # Fallback if the above logic fails
                return "Could not extract article text."
        else:
            return f"Failed to fetch URL. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred while fetching article: {e}"


def run_harvester():
    """The main function to run the complete harvesting process."""
    api_articles = fetch_news_from_api()
    scraped_articles = scrape_news_from_website()
    
    all_articles_metadata = api_articles + scraped_articles
    print(f"\n--- Found {len(all_articles_metadata)} total articles. Now fetching full content... ---")
    
    final_articles = []
    processed_urls = set()
    
    for article_meta in all_articles_metadata:
        url = article_meta['url']
        if url and url not in processed_urls:
            print(f"Processing: {article_meta['headline']}")
            content = fetch_full_article_text(url)
            
            if content and not content.startswith("Error"):
                article_meta['content'] = content
                final_articles.append(article_meta)
                processed_urls.add(url)
    
    return final_articles
    
# --- UPDATE MAIN EXECUTION ---
if __name__ == "__main__":
    articles = run_harvester()
    print(f"\n--- Harvesting Complete! Found {len(articles)} processable articles. ---")
    if articles:
        print("\n--- Example of a fully harvested article ---")
        print(articles[0])