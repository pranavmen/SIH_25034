# Save this as create_faiss_index.py
# You will need to install faiss: pip install faiss-cpu (or faiss-gpu for CUDA)

import csv
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def create_internship_text(internship):
    title = internship.get('Title', 'an internship role')
    skills = internship.get('Skills', 'various skills')
    return f"Seeking an intern for a {title} position. The ideal candidate should have experience in skills such as {skills}."

# 1. Load the Model
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
print(f"Loading model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded.")

# 2. Load CSV and prepare texts
# 2. Load CSV and prepare texts
# 2. Load CSV and prepare texts
all_internships = []

# --- THE FIX: Manually define the column headers ---
# Based on your screenshot, these appear to be the correct headers.
# Adjust them if you have more columns.
column_names = ['id', 'Title', 'Locations', 'Skills'] 

with open('internships.csv', mode='r', encoding='utf-8') as csvfile:
    # First, skip the original (and flawed) header row from the file
    next(csvfile) 
    
    # Now, use our manually defined column_names
    reader = csv.DictReader(csvfile, fieldnames=column_names)
    
    for row in reader:
        all_internships.append(row)

print(f"Loaded {len(all_internships)} internships.")
internship_texts = [create_internship_text(internship) for internship in all_internships]

# 3. Generate all embeddings
print("Generating embeddings for all internships...")
all_embeddings = model.encode(internship_texts, convert_to_numpy=True, show_progress_bar=True)
# Ensure embeddings are normalized for cosine similarity search
faiss.normalize_L2(all_embeddings)

# 4. Build and save the FAISS Index
embedding_dimension = all_embeddings.shape[1]
# We use IndexFlatIP, which is equivalent to cosine similarity for normalized vectors
index = faiss.IndexFlatIP(embedding_dimension) 
index.add(all_embeddings)
print(f"FAISS index built with {index.ntotal} vectors.")

faiss.write_index(index, 'internships.faiss')

# 5. Save the mapping from index position to our internship ID
index_to_id_map = {i: internship['id'] for i, internship in enumerate(all_internships)}
with open('index_to_id.pkl', 'wb') as f:
    pickle.dump(index_to_id_map, f)

print("✅ FAISS index and ID map saved successfully.")