from django.shortcuts import render
from .RecipeParser import get_ingredients

def index(request):
    ingredients = get_ingredients("https://www.bbcgoodfood.com/recipes/lemon-layer-cake-with-soft-cheese-icing")
    tesco_total_price = 4.50
    asda_total_price = 4.60

    context = {
        'ingredients': ingredients,
        'tesco_total_price': tesco_total_price,
        'asda_total_price': asda_total_price,
    }
    
    return render(request, "drpapp/index.html", context)
