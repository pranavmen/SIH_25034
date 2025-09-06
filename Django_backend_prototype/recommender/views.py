# recommender/views.py

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Internship
from .serializers import InternshipSerializer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from django.db.models import Q
import re
from rest_framework.exceptions import APIException

# A simple dictionary to hold pre-found YouTube tutorial links for skills
YOUTUBE_TUTORIALS = {
    'python': 'https://www.youtube.com/watch?v=eWRfhZUzrAc',
    'java': 'https://www.youtube.com/watch?v=grEKMHGYCs8',
    'marketing': 'https://www.youtube.com/watch?v=nU-IIXBWlS4',
    'sales': 'https://www.youtube.com/watch?v=bSa0_Vp3o_M',
    'ms office': 'https://www.youtube.com/watch?v=2-h6t4p6a_g',
    'data analysis': 'https://www.youtube.com/watch?v=rCG36C4d3g8',
    'communication': 'https://www.youtube.com/watch?v=Jwyb7I_3R2Y',
    'teamwork': 'https://www.youtube.com/watch?v=s8a8aV3w7pU',
    # Add other skills and links as needed
}

def get_youtube_link(skill):
    """Finds a relevant YouTube link for a given skill."""
    # Simple lookup, can be expanded with more advanced search if needed
    return YOUTUBE_TUTORIALS.get(skill.lower().replace(" ", ""), "https://www.youtube.com/results?search_query=how+to+learn+" + skill)

def generate_learning_roadmap():
    """Generates a generic learning roadmap."""
    return [
        "1. **Understand the Fundamentals:** Start with beginner tutorials to grasp the basic concepts.",
        "2. **Hands-On Practice:** Apply what you've learned by working on small projects or exercises.",
        "3. **Build a Project:** Create a simple, complete project to solidify your understanding.",
        "4. **Seek Feedback:** Share your work with others to get constructive feedback and improve.",
        "5. **Contribute & Collaborate:** Join online communities or contribute to open-source projects to learn from others."
    ]

def index(request):
    return render(request, 'recommender/index.html')

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@api_view(['POST'])
def recommend_internships(request):
    try:
        user_data = request.data
        user_skills = user_data.get('skills', [])
        user_interests = user_data.get('interests', [])
        user_location = user_data.get('location')
        user_wfh = user_data.get('wfhOnly')

        user_profile_text = ' '.join(user_skills) + ' ' + ' '.join(user_interests)

        base_query = Q()
        if user_wfh:
            base_query &= Q(location__icontains="Work From Home")
        elif user_location and user_location != "Any":
            base_query &= Q(location__icontains=user_location)

        internships = Internship.objects.filter(base_query)

        if not internships:
            return Response([], status=200)

        internship_data = list(internships.values('id', 'title', 'skills', 'interests', 'description'))
        df = pd.DataFrame(internship_data)

        if df.empty:
            return Response([], status=200)

        df['combined_features'] = df['skills'] + ' ' + df['interests'] + ' ' + df['title'] + ' ' + df['description']

        internship_embeddings = model.encode(df['combined_features'].tolist())
        user_profile_embedding = model.encode([user_profile_text])

        cosine_similarities = cosine_similarity(user_profile_embedding, internship_embeddings)
        similarity_scores = list(enumerate(cosine_similarities[0]))
        sorted_internships = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_internships_indices = [i[0] for i in sorted_internships[:5]]

        recommended_internships_ids = df.iloc[top_internships_indices]['id'].tolist()

        recommended_internships = sorted(
            Internship.objects.filter(id__in=recommended_internships_ids),
            key=lambda x: recommended_internships_ids.index(x.id)
        )

        serializer = InternshipSerializer(recommended_internships, many=True)
        response_data = serializer.data

        # --- New Feature Logic ---
        user_skills_set = set(skill.lower() for skill in user_skills)

        for internship_data in response_data:
            internship_skills_str = internship_data.get('skills', '')
            # Split skills by comma and strip whitespace
            internship_skills = set(skill.strip().lower() for skill in re.split(r'[, ]+', internship_skills_str) if skill)


            if not internship_skills:
                match_percentage = 0
                missing_skills = []
            else:
                matching_skills = user_skills_set.intersection(internship_skills)
                missing_skills_set = internship_skills.difference(user_skills_set)
                match_percentage = int((len(matching_skills) / len(internship_skills)) * 100) if internship_skills else 0
                missing_skills = list(missing_skills_set)


            # Generate a more detailed match reason
            reason = f"This internship is a great fit because it aligns with your interest in **{internship_data.get('interests', 'various sectors')}**."
            if matching_skills:
                reason += f" It also matches your skills in **{', '.join(list(matching_skills))}**."


            internship_data['match_percentage'] = match_percentage
            internship_data['match_reason'] = reason
            internship_data['missing_skills'] = [
                {
                    'skill': skill.title(),
                    'youtube_link': get_youtube_link(skill),
                    'roadmap': generate_learning_roadmap()
                } for skill in missing_skills
            ]


        return Response(response_data, status=200)

    except (APIException, KeyError, TypeError) as e:
        print(f"A validation or data error occurred: {e}")
        return Response({'error': 'Invalid data provided. Please check your input.'}, status=400)
    except Exception as e:
        # A general catch-all for unexpected server errors
        print(f"An unexpected server error occurred: {e}")
        return Response({'error': 'An unexpected error occurred on the server.'}, status=500)