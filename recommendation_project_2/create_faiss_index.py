import os
import csv
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --- This script should be in the project root ---

def create_internship_text(internship):
    title = internship.get('Title', 'an internship role')
    skills = internship.get('Skills', 'various skills')
    return f"Seeking an intern for a {title} position. The ideal candidate should have experience in skills such as {skills}."

# 1. Load the Model
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
print(f"Loading model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded.")

# 2. Define file paths
ASSET_PATH = os.path.join('recommender', 'ml_assets')
CSV_PATH = os.path.join(ASSET_PATH, 'internships.csv')

# 3. Load CSV and prepare texts
all_internships = []
column_names = ['id', 'Title', 'Locations', 'Skills']
with open(CSV_PATH, mode='r', encoding='utf-8') as csvfile:
    next(csvfile) # Skip the flawed header
    reader = csv.DictReader(csvfile, fieldnames=column_names)
    for row in reader:
        all_internships.append(row)
print(f"Loaded {len(all_internships)} internships.")

internship_texts = [create_internship_text(internship) for internship in all_internships]

# 4. Generate all embeddings
print("Generating embeddings for all internships...")
all_embeddings = model.encode(internship_texts, convert_to_numpy=True, show_progress_bar=True)
faiss.normalize_L2(all_embeddings)

# 5. Build and save the FAISS Index
embedding_dimension = all_embeddings.shape[1]
index = faiss.IndexFlatIP(embedding_dimension)
index.add(all_embeddings)
faiss.write_index(index, os.path.join(ASSET_PATH, 'internships.faiss'))
print(f"FAISS index built with {index.ntotal} vectors.")

# 6. Save the ID map
index_to_id_map = {i: internship['id'] for i, internship in enumerate(all_internships)}
with open(os.path.join(ASSET_PATH, 'index_to_id.pkl'), 'wb') as f:
    pickle.dump(index_to_id_map, f)

print("✅ FAISS index and ID map saved successfully to recommender/ml_assets/")