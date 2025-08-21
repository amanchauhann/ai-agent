# agent2_cleaner.py

# import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Load the spaCy English model
# nlp = spacy.load('en_core_web_sm')
# Import Flair
from flair.data import Sentence
from flair.models import SequenceTagger
# Load the Flair NER model (it will download on first run)
tagger = SequenceTagger.load('ner-english-ontonotes-fast')

# Get the list of English stop words
stop_words = set(stopwords.words('english'))

class CleanerTaggerAgent:
    def __init__(self):
        print("Cleaner & Tagger Agent is ready (using Flair).")

    def clean_text(self, text):
        """Removes noise, special characters, and extra whitespace."""
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = text.lower()
        text = ' '.join(text.split())
        return text

def extract_entities(self, text):
        """Uses Flair to extract named entities."""
        sentence = Sentence(text)
        tagger.predict(sentence)
        
        entities = {}
        for entity in sentence.get_spans('ner'):
            label = entity.tag  # e.g., 'PER', 'ORG', 'LOC'
            entity_text = entity.text
            
            # Normalize labels to match our previous format if desired
            if label in ['PER', 'PERSON']:
                label = 'PERSON'
            elif label in ['ORG', 'CORPORATION']:
                label = 'ORG'
            elif label in ['LOC', 'GPE']:
                label = 'GPE'

            if label in ['PERSON', 'ORG', 'GPE']:
                if label not in entities:
                    entities[label] = []
                if entity_text not in entities[label]:
                    entities[label].append(entity_text)
        return entities

    def categorize_article(self, text):
        """Assigns a category based on keywords found in the text."""
        text = text.lower() # Use lowercase text for matching
        
        # Define keywords for each category
        categories = {
            'Technology': ['ai', 'tech', 'apple', 'google', 'microsoft', 'software', 'startup'],
            'Business': ['stock', 'market', 'ceo', 'company', 'economy', 'finance', 'inc'],
            'Sports': ['game', 'team', 'player', 'score', 'match', 'league'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'virus']
        }
        
        # Count keyword occurrences for each category
        category_scores = {cat: 0 for cat in categories}
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    category_scores[category] += 1
                    
        # Find the category with the highest score
        # The max function with a key returns the key with the highest value
        top_category = max(category_scores, key=category_scores.get)
        
        # Only assign the category if at least one keyword was found
        if category_scores[top_category] > 0:
            return top_category
        else:
            return 'General'

    def process_article(self, article):
        """The main function to process a single article dictionary."""
        raw_content = article.get('content', '')
        
        # 1. Clean the text
        clean_content = self.clean_text(raw_content)
        
        # 2. Extract Entities from raw text
        entities = self.extract_entities(raw_content)
        
        # 3. Categorize using clean text
        category = self.categorize_article(clean_content)
        
        # Update the article dictionary
        article['clean_content'] = clean_content
        article['entities'] = entities
        article['category'] = category # Add the category
        
        return article

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # This is a sample output from Agent 1
    sample_article = {
        'source': 'Example News',
        'headline': 'Big Tech Announces New AI!',
        'url': 'http://example.com/news1',
        'content': 'New York, USA -- Big Tech Inc. today announced a revolutionary new AI.  \n\nRead more at http://example.com/promo. The stock for BTI surged 20%. The CEO, Jane Doe, was thrilled.'
    }

    # Create an instance of our agent
    agent = CleanerTaggerAgent()
    
    # Process the article
    processed_article = agent.process_article(sample_article)
    
    print("\n--- Original Content ---")
    print(sample_article['content'])
    
    print("\n--- Cleaned Content ---")
    print(processed_article)