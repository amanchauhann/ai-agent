# agent3_summarizer.py

import google.generativeai as genai

# --- CONFIGURATION ---
# IMPORTANT: Store your key securely. Don't hardcode it in production.
# For this example, we'll place it here.
# Replace 'YOUR_GEMINI_API_KEY' with the key you got from Google AI Studio.
GEMINI_API_KEY = 'AIzaSyBonC2x57rmdMCIS19-_FD9MiAvP74mRhM'

# Configure the generative AI library with your key
genai.configure(api_key=GEMINI_API_KEY)

class SummarizerAgent:
    def __init__(self):
        # Initialize the Gemini Pro model
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        print("Summarizer Agent is ready and connected to Gemini.")

    def summarize_article(self, article):
        """
        Generates a summary for the article's content using the Gemini model.
        """
        # We need the clean content from Agent 2
        content_to_summarize = article.get('clean_content')
        
        if not content_to_summarize:
            print("Warning: No content to summarize.")
            article['summary'] = "Error: No content provided for summarization."
            return article
            
        # This is our "prompt" - the instruction we give to the AI
        prompt = f"""
        Summarize the following news article into a neutral, factual summary of 60 words or less.
        Focus only on the key facts (who, what, where, when) and remove any opinionated language.

        Article: "{content_to_summarize}"

        Summary:
        """
        
        try:
            # Send the prompt to the model
            response = self.model.generate_content(prompt)
            
            # Extract the summary text from the response
            summary = response.text.strip()
            
            # Add the summary to our article dictionary
            article['summary'] = summary
            
        except Exception as e:
            print(f"An error occurred during summarization: {e}")
            article['summary'] = f"Error: Could not generate summary. {e}"
            
        return article

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # This is a sample output from Agent 2
    processed_article = {
        'source': 'Example News',
        'headline': 'Big Tech Announces New AI!',
        'url': 'http://example.com/news1',
        'content': 'New York, USA -- Big Tech Inc. today announced a revolutionary new AI.  \n\nRead more at http://example.com/promo. The stock for BTI surged 20%. The CEO, Jane Doe, was thrilled.',
        'clean_content': 'new york usa big tech inc today announced a revolutionary new ai read more at the stock for bti surged 20 the ceo jane doe was thrilled',
        'entities': {
            'GPE': ['New York', 'USA', 'AI'],
            'ORG': ['BTI'],
            'PERSON': ['Jane Doe']
        },
        'category': 'Business'
    }

    # Create an instance of our agent
    summarizer_agent = SummarizerAgent()
    
    # Generate the summary
    final_article = summarizer_agent.summarize_article(processed_article)
    
    print("\n--- Final, Enriched Article ---")
    import json
    # Use json.dumps for pretty printing the dictionary
    print(json.dumps(final_article, indent=2))