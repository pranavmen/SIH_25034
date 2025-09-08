from rest_framework import serializers

class InternshipSerializer(serializers.Serializer):
    Title = serializers.CharField()
    Locations = serializers.CharField()
    Skills = serializers.CharField()
    id = serializers.CharField()

class RecommendationSerializer(serializers.Serializer):
    final_score = serializers.FloatField()
    internship = InternshipSerializer()