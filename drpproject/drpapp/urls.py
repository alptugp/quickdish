from django.urls import path

from . import views

urlpatterns = [
    # Homepage
    path("", views.index, name="index"),
    # Comparison
    path("comparison/", views.comparison, name="comparison"),
    # Recommendations
    path("recommendations/", views.recommendations, name="recommendations"),
    path("recommendations_ve/", views.recommendations_vegan, name="recommendations_ve"),
    path("recommendations_v/", views.recommendations_vegetarian, name="recommendations_v"),
    path("recommendations_gf/", views.recommendations_gluten_free, name="recommendations_gf"),
]
