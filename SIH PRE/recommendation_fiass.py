import csv
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def calculate_keyword_score(student_skills, internship_skills):
    student_set = set([skill.strip().lower() for skill in student_skills.split(',')])
    internship_set = set([skill.strip().lower() for skill in internship_skills.split(',')])
    intersection = student_set.intersection(internship_set)
    union = student_set.union(internship_set)
    return 0.0 if not union else len(intersection) / len(union)

# Load all data into memory for quick lookups
all_internships_map = {}
column_names = ['id', 'Title', 'Locations', 'Skills'] # Manually define headers
with open('internships.csv', mode='r', encoding='utf-8') as csvfile:
    next(csvfile) # Skip the flawed header row
    reader = csv.DictReader(csvfile, fieldnames=column_names)
    for row in reader:
        all_internships_map[row['id']] = row

# --- CORE LOGIC with FAISS ---
def find_recommendations_faiss(student_profile, model, index, index_to_id_map):
    print(f"\n🔎 Finding recommendations for a student in '{student_profile['location_preference']}'...")
    
    student_text = f"A student with key skills in: {student_profile['skills']}."
    student_embedding = model.encode([student_text], convert_to_numpy=True)
    faiss.normalize_L2(student_embedding)

    k = 200 # Retrieve a large pool of skill-matched candidates
    distances, indices = index.search(student_embedding, k)
    
    all_top_candidates = []
    for i, idx in enumerate(indices[0]):
        if idx == -1: continue
            
        internship_id = index_to_id_map[idx]
        internship = all_internships_map[internship_id]
        
        sem_score = distances[0][i]
        key_score = calculate_keyword_score(student_profile['skills'], internship.get('Skills', ''))
        final_score = (0.6 * sem_score) + (0.4 * key_score)
        
        all_top_candidates.append({'final_score': final_score, 'internship': internship})

    recommendations_in_location = [
        rec for rec in all_top_candidates 
        if rec['internship']['Locations'].lower().strip() == student_profile['location_preference'].lower()
    ]
    
    return recommendations_in_location, all_top_candidates

# --- MAIN EXECUTION BLOCK (MODIFIED FOR GUARANTEED FALLBACK) ---
if __name__ == "__main__":
    MINIMUM_SCORE_THRESHOLD = 0.50
    FALLBACK_COUNT = 3
    
    # Load model, FAISS index, and maps
    print("Loading model and FAISS index...")
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    index = faiss.read_index('internships.faiss')
    with open('index_to_id.pkl', 'rb') as f:
        index_to_id_map = pickle.load(f)
    print("✅ Ready to make recommendations.")
    
    print("\n--- Enter Your Preferences ---")
    user_skills = input("Enter your skills (separated by commas): ")
    user_location = input("Enter your preferred location: ")

    student = {
        'skills': user_skills,
        'location_preference': user_location.strip()
    }

    in_location_recs, global_recs = find_recommendations_faiss(student, model, index, index_to_id_map)
    
    good_in_location = [rec for rec in in_location_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]
    good_global = [rec for rec in global_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]

    print("\n--- 🏆 Top Internship Recommendations ---")
    
    # ** NEW DISPLAY LOGIC WITH GUARANTEED FALLBACK **
    if good_in_location:
        print(f"Displaying top matches in your preferred location: {student['location_preference']}")
        for rec in good_in_location[:5]:
            details = rec['internship']
            print(f"\nFinal Score: {rec['final_score']:.4f}")
            print(f"  Title: {details['Title']}")
            print(f"  Skills: {details['Skills']}")
            print(f"  Location: {details['Locations']}")
    
    elif good_global:
        print(f"\nℹ️ No ideal matches were found in {student['location_preference']}.")
        print(f"Here are the {FALLBACK_COUNT} best matches from other locations:")
        for rec in good_global[:FALLBACK_COUNT]:
            details = rec['internship']
            print(f"\nScore: {rec['final_score']:.4f} (Best Alternative)")
            print(f"  Title: {details['Title']}")
            print(f"  Skills: {details['Skills']}")
            print(f"  Location: {details['Locations']}")
            
    # Ultimate Fallback: If no good matches are found anywhere, show the top 3 global closest matches
    elif global_recs:
        print(f"\nℹ️ No ideal matches were found anywhere. Here are the top {FALLBACK_COUNT} closest skill matches from all locations:")
        for rec in global_recs[:FALLBACK_COUNT]:
            details = rec['internship']
            print(f"\nScore: {rec['final_score']:.4f} (Closest Skill Match)")
            print(f"  Title: {details['Title']}")
            print(f"  Skills: {details['Skills']}")
            print(f"  Location: {details['Locations']}")
            
    else:
        # This case should now be extremely rare
        print(f"\nℹ️ Could not find any internships to recommend.")