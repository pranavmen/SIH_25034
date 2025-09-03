import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- All functions now use the new model ---

def create_advanced_model(data_path='internships.csv'):
    """
    Loads data and creates recommendation components using a pre-trained model.
    """
    df = pd.read_csv(data_path)
    df['Skills'] = df['Skills'].fillna('')
    
    # 1. Load a powerful pre-trained model
    # This model is great for understanding short text like skills.
    # The first time you run this, it will download the model (a few hundred MB).
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Convert all internship skills into numerical vectors (embeddings)
    # This might take a moment the first time.
    print("Creating skill embeddings... (This may take a moment)")
    skill_embeddings = model.encode(df['Skills'].tolist(), show_progress_bar=True)
    
    print("Advanced recommendation model created successfully.")
    return df, model, skill_embeddings

def get_advanced_recommendations(user_skills, df, model, skill_embeddings, top_n=5):
    """
    Recommends internships by comparing semantic meaning.
    """
    # Convert the user's query into a vector
    user_embedding = model.encode([user_skills])
    
    # Calculate cosine similarity between user's skills and all internships
    cosine_similarities = cosine_similarity(user_embedding, skill_embeddings).flatten()
    
    # Get the top N internships
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    
    recommendations_df = df.iloc[top_indices]
    return recommendations_df

# --- Main execution block ---
if __name__ == '__main__':
    # Create the model ONCE at the start
    internship_df, model, skill_embeddings = create_advanced_model('internships.csv')
    
    if internship_df is not None:
        # Loop to allow multiple queries
        while True:
            my_skills_input = input("\n▶ Enter your skills (or type 'exit' to quit): ")
            
            if my_skills_input.lower() == 'exit':
                break
            
            # Get recommendations using the new advanced function
            recommendations = get_advanced_recommendations(my_skills_input, internship_df, model, skill_embeddings)
            
            print(f"\nTOP 5 RECOMMENDATIONS FOR: '{my_skills_input}'")
            print("="*50)

            if recommendations.empty:
                print("Sorry, no matching internships found.")
            else:
                for index, row in recommendations.iterrows():
                    print(f"Title: {row['Title']}")
                    print(f"Company: {row['Company']}")
                    print(f"Skills: {row['Skills']}")
                    print(f"Location: {row['Location']}")
                    print("-" * 30)