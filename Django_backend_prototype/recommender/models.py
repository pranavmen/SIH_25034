# recommender/models.py
from django.db import models

class Internship(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    stipend = models.CharField(max_length=50)
    description = models.TextField()
    apply_link = models.URLField()
    skills = models.CharField(max_length=255, help_text="Comma-separated skills")
    interests = models.CharField(max_length=255, help_text="Comma-separated interests")

    def __str__(self):
        return self.title