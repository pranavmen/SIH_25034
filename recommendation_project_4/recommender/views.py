from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.core.cache import cache  # <-- Import Django's cache
from .engine import engine
from .serializers import RecommendationSerializer


class HomePageView(TemplateView):
    template_name = "index.html"


class RecommendInternships(APIView):
    def get(self, request, *args, **kwargs):
        skills = request.query_params.get('skills', '')
        location = request.query_params.get('location', '')
        interest = request.query_params.get('interest', '')

        if not skills or not location:
            return Response({"error": "Please provide both 'skills' and 'location' parameters."}, status=400)

        # --- CACHING LOGIC ---
        # 1. Create a unique key for this request
        cache_key = f"rec_{skills}_{location}_{interest}"

        # 2. Try to get the result from the cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            print("✅ Returning response from cache!")
            return Response(cached_result)

        # 3. If not in cache, calculate the result as before
        print("❌ Cache miss. Calculating new recommendations...")
        in_location_recs, global_recs = engine.find_recommendations(skills, location, interest)

        # ... (rest of your fallback and filtering logic is the same)
        MINIMUM_SCORE_THRESHOLD = 0.55
        FALLBACK_COUNT = 3

        good_in_location = [rec for rec in in_location_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]
        good_global = [rec for rec in global_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]

        results = []
        message = ""

        if good_in_location:
            message = f"Top matches in your preferred location: {location}"
            results = good_in_location[:5]
        elif good_global:
            message = f"No ideal matches found in {location}. Here are the best matches from other locations:"
            results = good_global[:FALLBACK_COUNT]
        else:
            message = f"No ideal matches were found anywhere. Here are the top {FALLBACK_COUNT} closest skill matches from all locations:"
            results = global_recs[:FALLBACK_COUNT]

        serializer = RecommendationSerializer(results, many=True)
        final_response_data = {
            "message": message,
            "recommendations": serializer.data
        }

        # 4. Save the new result to the cache for 1 hour (3600 seconds)
        cache.set(cache_key, final_response_data, timeout=3600)

        return Response(final_response_data)