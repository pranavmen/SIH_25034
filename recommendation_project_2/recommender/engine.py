import os
import csv
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings
import numpy as np


# This helper function is no longer the primary score, but a small component
def calculate_keyword_score(student_skills, internship_skills):
    student_set = set([skill.strip().lower() for skill in student_skills.split(',')])
    internship_set = set([skill.strip().lower() for skill in (internship_skills or "").split(',')])
    intersection = student_set.intersection(internship_set)
    union = student_set.union(internship_set)
    return 0.0 if not union else len(intersection) / len(union)


class RecommendationEngine:
    def __init__(self):
        print("Loading recommendation engine assets...")
        asset_path = os.path.join(settings.BASE_DIR, 'recommender', 'ml_assets')
        model_name = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'

        self.model = SentenceTransformer(model_name)
        self.index = faiss.read_index(os.path.join(asset_path, 'internships.faiss'))

        with open(os.path.join(asset_path, 'index_to_id.pkl'), 'rb') as f:
            self.index_to_id_map = pickle.load(f)

        self.all_internships_map = {}
        column_names = ['id', 'Title', 'Locations', 'Skills']
        with open(os.path.join(asset_path, 'internships.csv'), mode='r', encoding='utf-8') as csvfile:
            next(csvfile)
            reader = csv.DictReader(csvfile, fieldnames=column_names)
            for row in reader:
                self.all_internships_map[row['id']] = row
        print("✅ Recommendation engine loaded successfully.")

    def find_recommendations(self, skills, location, interest):
        # Combine skills and interest for the main semantic query
        if interest:
            student_text = f"A student with key skills in: {skills}. They are interested in an internship where they can {interest}."
        else:
            student_text = f"A student with key skills in: {skills}."

        student_embedding = self.model.encode([student_text], convert_to_numpy=True)
        faiss.normalize_L2(student_embedding)

        # FAISS search finds semantically similar candidates
        k = 200
        distances, indices = self.index.search(student_embedding, k)

        all_top_candidates = []
        # Create a clean list of the user's explicit skills for boosting
        user_explicit_skills = [s.strip().lower() for s in skills.split(',')]

        for i, idx in enumerate(indices[0]):
            if idx == -1: continue

            internship_id = self.index_to_id_map[idx]
            internship = self.all_internships_map[internship_id]

            sem_score = distances[0][i]

            # --- NEW: Aggressive Skill Boost Calculation ---
            skill_boost_score = 0
            internship_skills_text = internship.get('Skills', '').lower()
            for skill in user_explicit_skills:
                if skill in internship_skills_text:
                    skill_boost_score += 1  # Add a point for each matching skill

            # Normalize the boost score by the number of skills the user provided
            normalized_boost = skill_boost_score / len(user_explicit_skills) if user_explicit_skills else 0

            # ** FINAL SCORING: Semantic score is primary, but the skill boost is very powerful **
            final_score = (0.7 * sem_score) + (0.3 * normalized_boost)

            all_top_candidates.append({'final_score': final_score, 'internship': internship})

        # Sort by the new, more balanced final score
        all_top_candidates.sort(key=lambda x: x['final_score'], reverse=True)

        # Filter by location after scoring
        recommendations_in_location = [
            rec for rec in all_top_candidates
            if rec['internship']['Locations'].lower().strip() == location.lower()
        ]

        return recommendations_in_location, all_top_candidates


# Instantiate the engine ONCE when Django starts
engine = RecommendationEngine()