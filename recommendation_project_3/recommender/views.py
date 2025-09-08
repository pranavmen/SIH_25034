from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from .engine import engine
from .serializers import RecommendationSerializer


class HomePageView(TemplateView):
    """
    A view that renders the main HTML page.
    """
    template_name = "index.html"


class RecommendInternships(APIView):
    """
    The main API endpoint for getting internship recommendations.
    """

    def get(self, request, *args, **kwargs):
        # 1. Get all three inputs from the request's query parameters
        skills = request.query_params.get('skills', '')
        location = request.query_params.get('location', '')
        interest = request.query_params.get('interest', '')

        if not skills or not location:
            return Response({"error": "Please provide both 'skills' and 'location' parameters."}, status=400)

        # 2. Pass all three inputs to the recommendation engine
        in_location_recs, global_recs = engine.find_recommendations(skills, location, interest)

        # 3. Define thresholds for filtering the results
        MINIMUM_SCORE_THRESHOLD = 0.55
        FALLBACK_COUNT = 3

        # 4. Filter results based on the score
        good_in_location = [rec for rec in in_location_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]
        good_global = [rec for rec in global_recs if rec['final_score'] >= MINIMUM_SCORE_THRESHOLD]

        results = []
        message = ""

        # 5. Apply the fallback logic to decide which results to show
        if good_in_location:
            message = f"Top matches in your preferred location: {location}"
            results = good_in_location[:5]
        elif good_global:
            message = f"No ideal matches found in {location}. Here are the best matches from other locations:"
            results = good_global[:FALLBACK_COUNT]
        elif global_recs:
            message = f"No ideal matches were found anywhere. Here are the top {FALLBACK_COUNT} closest skill matches from all locations:"
            results = global_recs[:FALLBACK_COUNT]
        else:
            message = "Could not find any internships to recommend."
            results = []

        # 6. Convert the final list to JSON and send it as a response
        serializer = RecommendationSerializer(results, many=True)
        return Response({"message": message, "recommendations": serializer.data})