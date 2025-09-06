# recommender/serializers.py

from rest_framework import serializers
from .models import Internship

class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        # Explicitly list the fields you want to expose in your API
        fields = '__all__'