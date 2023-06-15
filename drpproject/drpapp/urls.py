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
    
    # Recipe saving
    path("recipe_saved/", views.save_recipe, name="recipe_saved"),
    path("all_saved_recipes/", views.show_all_recipes, name="all_saved_recipes"),

    # Proxy
    path("proxy_tesco_basket/", views.proxy_tesco_basket, name="proxy_tesco_basket"),
    
    # Dead Click logging
    path('log-dead-click/', views.log_dead_click, name='log_dead_click'),
    
    # Dead Clicks Dashboard
    path('dead-clicks/', views.dead_clicks_list, name='dead_clicks_list'),
]
