from django.urls import path
from .views import RecommendInternships, HomePageView, InternshipAnalyticsView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('api/recommend/', RecommendInternships.as_view(), name='recommend-internships'),
    path('api/analytics/', InternshipAnalyticsView.as_view(), name='internship-analytics'),
]