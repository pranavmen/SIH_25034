import csv
from sentence_transformers import SentenceTransformer, util

# --- HELPER FUNCTIONS ---

def create_internship_text(internship):
    """Creates a more natural, descriptive sentence from internship data."""
    title = internship.get('Title', 'an internship role')
    skills = internship.get('Skills', 'various skills')
    return f"Seeking an intern for a {title} position. The ideal candidate should have experience in skills such as {skills}."

def calculate_keyword_score(student_skills, internship_skills):
    """Calculates a score based on the overlap of skills (Jaccard Similarity)."""
    student_set = set([skill.strip().lower() for skill in student_skills.split(',')])
    internship_set = set([skill.strip().lower() for skill in internship_skills.split(',')])
    
    intersection = student_set.intersection(internship_set)
    union = student_set.union(internship_set)
    
    return 0.0 if not union else len(intersection) / len(union)

# --- CORE LOGIC ---

def load_internships_from_csv(filepath):
    """Loads internship data from a CSV file."""
    internships = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                internships.append(row)
        print(f"✅ Successfully loaded {len(internships)} internships from {filepath}")
    except FileNotFoundError:
        print(f"❌ Error: The file {filepath} was not found.")
        return None
    return internships

def find_recommendations(student_profile, all_internships, model):
    """Calculates and returns a sorted list of all potential recommendations."""
    print(f"\n🔎 Finding recommendations for a student in '{student_profile['location_preference']}'...")

    filtered_internships = [
        internship for internship in all_internships
        if internship['Location'].lower() == student_profile['location_preference'].lower()
    ]

    if not filtered_internships:
        # This case is handled in the main block now, but we can keep a check here.
        return [], 0 

    # Step 2A: Prepare text using the richer function
    student_text = f"A student with key skills in: {student_profile['skills']}."
    internship_texts = [create_internship_text(internship) for internship in filtered_internships]

    # Step 2B: Generate semantic embeddings
    print("🧠 Generating semantic embeddings...")
    student_embedding = model.encode(student_text, convert_to_tensor=True)
    internship_embeddings = model.encode(internship_texts, convert_to_tensor=True)
    semantic_scores = util.cos_sim(student_embedding, internship_embeddings)

    # Step 3: Combine scores and rank
    recommendations = []
    for i, internship in enumerate(filtered_internships):
        sem_score = semantic_scores[0][i].item()
        key_score = calculate_keyword_score(student_profile['skills'], internship.get('Skills', ''))
        final_score = (0.6 * sem_score) + (0.4 * key_score)
        
        recommendations.append({
            'final_score': final_score,
            'internship': internship 
        })

    sorted_recommendations = sorted(recommendations, key=lambda x: x['final_score'], reverse=True)
    
    return sorted_recommendations, len(filtered_internships)

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    
    # This is the quality gate. Adjust this value as needed.
    MINIMUM_SCORE_THRESHOLD = 0.40

    print("Loading the sentence transformer model...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("Model loaded.")
    
    internships = load_internships_from_csv('internships.csv')

    if internships:
        student = {
            'skills': 'Python, Machine Learning, PyTorch, SQL, data analysis, Pandas',
            'location_preference': 'Work From Home'
        }

        # Get all potential recommendations, regardless of score
        all_recommendations, jobs_found_in_location = find_recommendations(student, internships, model)

        # ** NEW: Filter the results based on the quality threshold **
        good_recommendations = [
            rec for rec in all_recommendations 
            if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD
        ]

        print("\n--- 🏆 Top Internship Recommendations ---")
        if good_recommendations:
            print(f"Displaying top matches above a score of {MINIMUM_SCORE_THRESHOLD}...")
            for rec in good_recommendations[:5]:
                details = rec['internship']
                print(f"\nFinal Score: {rec['final_score']:.4f}")
                print(f"  Title: {details['Title']}")
                print(f"  Skills: {details['Skills']}")
                print(f"  Location: {details['Location']}")
        elif jobs_found_in_location > 0:
            # This is the new message if jobs exist but none are a good match
            print(f"\nℹ️ We found {jobs_found_in_location} jobs in {student['location_preference']}, but none were a good match for your skills.")
        else:
            # This message appears if no jobs were found in the location at all
            print(f"\nℹ️ No jobs were found for your preferred location: {student['location_preference']}.")