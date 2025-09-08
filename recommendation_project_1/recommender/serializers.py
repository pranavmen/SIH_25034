from rest_framework import serializers

class InternshipSerializer(serializers.Serializer):
    Title = serializers.CharField()
    Locations = serializers.CharField()
    Skills = serializers.CharField()
    id = serializers.CharField()

class RecommendationSerializer(serializers.Serializer):
    final_score = serializers.FloatField()
    internship = InternshipSerializer()
    # Add the new fields here
    matching_skills = serializers.IntegerField()
    matched_skills_list = serializers.ListField(child=serializers.CharField())