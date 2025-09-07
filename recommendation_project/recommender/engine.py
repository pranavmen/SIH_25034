import os
import csv
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings


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

    def find_recommendations(self, skills, location):
        student_text = f"A student with key skills in: {skills}."
        student_embedding = self.model.encode([student_text])
        faiss.normalize_L2(student_embedding)

        k = 200
        distances, indices = self.index.search(student_embedding, k)

        all_top_candidates = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            internship_id = self.index_to_id_map[idx]
            internship = self.all_internships_map[internship_id]
            sem_score = distances[0][i]
            key_score = calculate_keyword_score(skills, internship.get('Skills'))
            final_score = (0.6 * sem_score) + (0.4 * key_score)
            all_top_candidates.append({'final_score': final_score, 'internship': internship})

        in_location_recs = [rec for rec in all_top_candidates if
                            rec['internship']['Locations'].lower().strip() == location.lower()]
        return in_location_recs, all_top_candidates


engine = RecommendationEngine()