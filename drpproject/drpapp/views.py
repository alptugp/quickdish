from django.shortcuts import render
from .RecipeParser import get_ingredients
from .TescoWebScraper import getMostRelevantItemTesco
from .AsdaWebScraper import getMostRelevantItemAsda
import multiprocessing
import concurrent.futures


def index(request):
    return render(request, "drpapp/index.html")

def comparison(request): 
    # Get what the user typed in the search bar (the recipe url) after they press the enter button
    query = request.GET.get('query', '')
    ingredients = get_ingredients(query)
    tesco_total_price, tesco_item_links = total_price_tesco(ingredients)
    asda_total_price, asda_item_links = total_price_asda(ingredients)

    context = {
        'ingredients': ingredients,
        'tesco_total_price': tesco_total_price,
        'asda_total_price': asda_total_price,
        'tesco_item_links': tesco_item_links,
        'asda_item_links': asda_item_links
    }
    
    return render(request, "drpapp/comparison.html", context)

def get_tesco_product_links(items):
    # A Tesco link looks like this: https://www.tesco.com/groceries/en-GB/products/<product-id>
    base_url = "https://www.tesco.com/groceries/en-GB/products/"
    for ingredient in items:
        items[ingredient] = base_url + items[ingredient]
    return items

def get_asda_product_links(items):
    # An ASDA link looks like this: https://groceries.asda.com/product/<product-id>
    base_url = "https://groceries.asda.com/product/"
    for ingredient in items:
        items[ingredient] = base_url + items[ingredient]
    return items
   

def tesco_worker(ingredient, items):
    most_relevant_item = getMostRelevantItemTesco(str(ingredient))
    price = most_relevant_item['price']
    price = round(float(price), 2)
    item_id = most_relevant_item['id']
    items[ingredient] = item_id
    return price

def asda_worker(ingredient, items):
    most_relevant_item = getMostRelevantItemAsda(str(ingredient))
    # price is a string of the form £<price> (not a string for the tesco api though)
    price_str = most_relevant_item['price']['price_info']['price']
    # remove the £ sign and convert to float (2dp)
    price = round(float(price_str[1:]), 2)
    item_id = most_relevant_item['inventory']['sku_id']
    print(ingredient) 
    print(most_relevant_item['item'])
    items[ingredient] = item_id
    return price

def total_price_tesco(ingredients):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(tesco_worker, ingredient, items) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0 
    for result in results:
        total_price += result.result()
    
    

    executor.shutdown()
    item_links = get_tesco_product_links(items)

    return total_price, item_links

def total_price_asda(ingredients):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(asda_worker, ingredient, items) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    item_links = get_asda_product_links(items)

    executor.shutdown()

    return total_price, item_links



