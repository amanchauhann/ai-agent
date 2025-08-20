# agent4_personalizer.py

def record_user_interaction(user_profile, article):
    """
    Updates a user's profile based on an article they interacted with.
    This simulates a user reading/liking an article.
    """
    # Increase score for the article's category
    category = article.get('category', 'General')
    if category not in user_profile['categories']:
        user_profile['categories'][category] = 0
    user_profile['categories'][category] += 1.0  # Increment category score

    # Increase score for each entity in the article
    entities = article.get('entities', {})
    for ent_type, ent_list in entities.items():
        for entity_name in ent_list:
            if entity_name not in user_profile['entities']:
                user_profile['entities'][entity_name] = 0
            user_profile['entities'][entity_name] += 0.5 # Increment entity score (less than category)
            
    return user_profile


class PersonalizationAgent:
    def __init__(self):
        print("Personalization Agent is ready.")

    def calculate_relevance_score(self, user_profile, article):
        """Calculates a relevance score for an article based on the user's profile."""
        score = 0.0
        
        # --- Scoring Logic ---
        # 1. Category Score
        article_category = article.get('category', 'General')
        if article_category in user_profile['categories']:
            score += user_profile['categories'][article_category] * 1.5 # Weight category matches higher

        # 2. Entity Score
        article_entities = article.get('entities', {})
        for ent_type, ent_list in article_entities.items():
            for entity_name in ent_list:
                if entity_name in user_profile['entities']:
                    score += user_profile['entities'][entity_name] * 1.0 # Weight entity matches

        return score

    def rank_articles_for_user(self, user_profile, articles):
        """Ranks a list of articles based on relevance scores."""
        
        scored_articles = []
        for article in articles:
            # Calculate score for each article
            score = self.calculate_relevance_score(user_profile, article)
            # Store the article and its score
            scored_articles.append({'article': article, 'score': score})
            
        # Sort the articles in descending order based on the score
        ranked_list = sorted(scored_articles, key=lambda x: x['score'], reverse=True)
        
        return ranked_list


        # agent4_personalizer.py (continued)

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # 1. Define a list of processed articles (output from Agent 3)
    sample_articles = [
        {
            "headline": "Google announces major breakthrough in quantum computing",
            "category": "Technology", "entities": {"ORG": ["Google"], "MISC": ["quantum computing"]}
        },
        {
            "headline": "World Health Organization releases new pandemic guidelines",
            "category": "Health", "entities": {"ORG": ["World Health Organization"]}
        },
        {
            "headline": "Apple's stock hits all-time high after iPhone launch",
            "category": "Business", "entities": {"ORG": ["Apple"], "PRODUCT": ["iPhone"]}
        },
        {
            "headline": "DeepMind, a subsidiary of Google, solves protein folding",
            "category": "Technology", "entities": {"ORG": ["DeepMind", "Google"]}
        }
    ]

    # 2. Start with an empty user profile
    user_profile = {
        "categories": {},
        "entities": {}
    }

    # 3. Simulate the user reading two 'Technology' articles about 'Google'
    print("--- Simulating User Behavior ---")
    print("User reads: 'Google announces major breakthrough in quantum computing'")
    user_profile = record_user_interaction(user_profile, sample_articles[0])
    print("User reads: 'DeepMind, a subsidiary of Google, solves protein folding'")
    user_profile = record_user_interaction(user_profile, sample_articles[3])
    
    print("\n--- Updated User Profile ---")
    import json
    print(json.dumps(user_profile, indent=2))

    # 4. Use the Personalization Agent to rank the articles
    print("\n--- Ranking Articles for the User ---")
    personalizer = PersonalizationAgent()
    ranked_articles = personalizer.rank_articles_for_user(user_profile, sample_articles)

    # 5. Display the personalized feed
    print("\n--- Your Personalized News Feed ---")
    for item in ranked_articles:
        score = item['score']
        headline = item['article']['headline']
        print(f"Score: {score:.2f} | {headline}")