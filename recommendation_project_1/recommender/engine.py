import os
import csv
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings
import numpy as np  # Ensure numpy is imported


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

    def find_recommendations(self, skills, location):
        # This entire method is replaced with your new logic
        student_profile = {'skills': skills, 'location_preference': location}
        student_text = f"A student with key skills in: {skills}."
        student_embedding = self.model.encode([student_text], convert_to_numpy=True)
        faiss.normalize_L2(student_embedding)

        k = 200
        distances, indices = self.index.search(student_embedding, k)

        all_top_candidates = []
        user_skills_list = [skill.strip().lower() for skill in skills.split(',')]

        for i, idx in enumerate(indices[0]):
            if idx == -1: continue

            internship_id = self.index_to_id_map[idx]
            internship = self.all_internships_map[internship_id]
            internship_skills_text = internship.get('Skills', '').lower()

            # New, more accurate skill matching
            matching_skills_count = 0
            matched_skills_list = []
            for skill in user_skills_list:
                if skill in internship_skills_text:
                    matching_skills_count += 1
                    matched_skills_list.append(skill)

            if matching_skills_count == 0:
                continue

            sem_score = distances[0][i]
            key_score = matching_skills_count / len(user_skills_list) if user_skills_list else 0
            final_score = (0.5 * sem_score) + (0.5 * key_score)

            all_top_candidates.append({
                'final_score': final_score,
                'internship': internship,
                'matching_skills': matching_skills_count,
                'matched_skills_list': matched_skills_list
            })

        # New, more accurate sorting: primarily by count of matching skills
        all_top_candidates.sort(key=lambda x: (x['matching_skills'], x['final_score']), reverse=True)

        recommendations_in_location = [
            rec for rec in all_top_candidates
            if rec['internship']['Locations'].lower().strip() == location.lower()
        ]

        return recommendations_in_location, all_top_candidates


# Instantiate the engine ONCE
engine = RecommendationEngine()