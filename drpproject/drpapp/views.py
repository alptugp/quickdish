from django.shortcuts import render
from .RecipeParser import get_ingredients
from .TescoWebScraper import getMostRelevantItemTesco
from .AsdaWebScraper import getMostRelevantItemAsda
import multiprocessing
import concurrent.futures


def index(request):
    ingredients = get_ingredients("https://www.bbcgoodfood.com/recipes/basic-omelette")
    tesco_total_price, tesco_items = total_price_tesco(ingredients)
    asda_total_price = 0 

    print(tesco_items)

    context = {
        'ingredients': ingredients,
        'tesco_total_price': tesco_total_price,
        'asda_total_price': asda_total_price,
        'tesco_items': tesco_items,
    }
    
    return render(request, "drpapp/index.html", context)

def total_price_tesco(ingredients):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(worker, ingredient, items) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0 
    for result in results:
        total_price += result.result()

    executor.shutdown()

    return total_price, items

def worker(ingredient, items):
    most_relevant_item = getMostRelevantItemTesco(str(ingredient))
    price = most_relevant_item['price']
    item_id = most_relevant_item['id']
    items[ingredient] = item_id
    return price

"""def total_price_asda(ingredients):
    total_price = 0
    for ingredient in ingredients:
        most_relevant_item = getMostRelevantItemAsda(ingredient)
        total_price += 1
    return total_price """



