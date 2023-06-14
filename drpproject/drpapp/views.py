from django.shortcuts import render, redirect
from .RecipeParser import get_recipe_details
from .TescoSearch import searchTesco
from .AsdaSearch import searchAsda
from .SainsburysSearch import searchSainsburys
from .MorrisonsSearch import search_morrisons
from .NLP import cleanupIngredients
#from .IngredientParser import cleanup_ingredients
from .models import DietForm, DietaryRestriction, IngredientsForm
import concurrent.futures
from django.http import JsonResponse
import requests
import random

dietary_preferences_key = 'dietary_preferences'
possible_preferences = [
    "vegan",
    "vegetarian",
    "gluten_free",
    "none",
]

number_of_supermarkets = 4

def index(request):
    saved_preferences = False
    recommendation = "none"
    
    # User has submitted new dietary preferences (arriving from index's form submission)
    if request.method == 'POST':
        saved_preferences = True
        diet_form = DietForm(request.POST)
        if diet_form.is_valid():
            preferences = diet_form.cleaned_data
            request.session[dietary_preferences_key] = preferences
            for rec in possible_preferences:
                if preferences.get(rec):
                    recommendation = rec
                    break
    
    # User is visiting the homepage (arriving from elsewhere)
    elif request.method == 'GET':
        if dietary_preferences_key in request.session:
            # Existing session
            preferences = request.session[dietary_preferences_key]
            diet_form = DietForm(preferences)
            for rec in possible_preferences:
                if preferences.get(rec):
                    recommendation = rec
                    break
        else:
            # New session
            diet_form = DietForm()
        
    random_recipes = ["https://www.bbcgoodfood.com/recipes/vegan-jambalaya", "https://www.bbcgoodfood.com/recipes/asian-chicken-noodle-soup"
                      , "https://www.bbcgoodfood.com/recipes/easy-chicken-curry", "https://www.bbcgoodfood.com/recipes/chow-mein"]
    random_recipe = random_recipes[random.randint(0, len(random_recipes) - 1)]
    
    context = {
        'diet_form': diet_form,
        'recommendation': recommendation,
        'saved_preferences': saved_preferences,
        'random_recipe': random_recipe,
    }
    
    return render(request, "drpapp/index.html", context=context)

def recommendations(request):
    return render(request, "drpapp/recommendations.html")
def recommendations_vegan(request):
    return render(request, "drpapp/recommendations_ve.html")
def recommendations_vegetarian(request):
    return render(request, "drpapp/recommendations_v.html")
def recommendations_gluten_free(request):
    return render(request, "drpapp/recommendations_gf.html")

def links_missing(links):
    print(links.values())
    return any(link[0] == 'INVALID' for link in links.values())

def get_comp_price(total_price, links):
    if links_missing(links):
        print("missing   !!!!!!!!")
        return float('inf')
    else:
        return float(total_price)

def comparison(request):
    original_ingredients_key = 'original_ingredients'
    full_ingredients_key = 'full_ingredients'
    new_ingredient_key = 'new_ingredient'
    original_ingredients = []
    full_ingredients = []
    ingredients = []

    # User updates the dietary preferences
    if request.method == 'POST':
        original_ingredients = request.session.get(original_ingredients_key, [])
        full_ingredients = request.session.get(full_ingredients_key, [])
        title = request.session.get('title', [])
        image = request.session.get('image', [])
        instrs = request.session.get('instrs', [])
        for key in request.POST.keys():
            if key != "csrfmiddlewaretoken":
                if key == new_ingredient_key:
                    new_ingredient = request.POST.get(new_ingredient_key)
                    if new_ingredient != "":
                        ingredients.append(new_ingredient)
                        full_ingredients.append(new_ingredient)
                        request.session[full_ingredients_key] = full_ingredients
                else:
                    ingredients.append(key)

        #STARTS HERE
        preferences = request.session.get('dietary_preferences')
        supermarket_functions = [
            total_price_sainsburys,
            total_price_asda,
            total_price_tesco,
            #total_price_morrisons,
        ]
        num_threads = len(supermarket_functions)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

        results = [executor.submit(fun, ingredients, preferences, request) for fun in supermarket_functions]
        concurrent.futures.wait(results)
        
        sainsburys_total_price, sainsburys_item_links = results[0].result()
        asda_total_price, asda_item_links = results[1].result()
        tesco_total_price, tesco_item_links = results[2].result()
        morrisons_total_price, morrisons_item_links = tesco_total_price, tesco_item_links #results[3].result()
        executor.shutdown()

        cheapest_total_market = get_cheapest_market([
            get_comp_price(sainsburys_total_price, sainsburys_item_links),
            get_comp_price(asda_total_price, asda_item_links),
            get_comp_price(morrisons_total_price, morrisons_item_links),
            get_comp_price(tesco_total_price, tesco_item_links)
        ])

        not_found_row_ingredients = []

        for i in range(1, number_of_supermarkets + 1): 
            for ingredient in ingredients:
                if len(list(filter(lambda x: x == "INVALID", [sainsburys_item_links[ingredient][0], 
                                                        asda_item_links[ingredient][0],
                                                        tesco_item_links[ingredient][0],
                                                        morrisons_item_links[ingredient][0]]))) == i: 
                    not_found_row_ingredients.insert(0, ingredient)

                    #invalid_item_links.update({ingredient: sainsburys_item_links[ingredient]})
        
        found_row_ingredients = [ingredient for ingredient in ingredients if ingredient not in not_found_row_ingredients] 

        asda_found_entries_total_price = round(sum([float(asda_item_links[ingredient][1][1:]) for ingredient in found_row_ingredients]), 2)
        tesco_found_entries_total_price = round(sum([float(tesco_item_links[ingredient][1][1:]) for ingredient in found_row_ingredients]), 2)
        sainsburys_found_entries_total_price = round(sum([float(sainsburys_item_links[ingredient][1][1:]) for ingredient in found_row_ingredients]), 2)
        morrisons_found_entries_total_price = round(sum([float(morrisons_item_links[ingredient][1][1:]) for ingredient in found_row_ingredients]), 2)
        cheapest_found_entries_market = get_cheapest_market([
                                                             sainsburys_found_entries_total_price, 
                                                             asda_found_entries_total_price, 
                                                             morrisons_found_entries_total_price, 
                                                             tesco_found_entries_total_price
                                                            ])

        show_table = True
        #ENDS HERE

    # User searches a recipe
    elif request.method == 'GET':
        query = request.GET.get('query', '')
        
        dietary_preferences = request.session.get('dietary_preferences')
        original_ingredients, title, image, instrs = get_recipe_details(query, dietary_preferences)
        title = title.title()
        full_ingredients = cleanupIngredients(original_ingredients)
        ingredients = full_ingredients
        request.session[original_ingredients_key] = original_ingredients
        request.session[full_ingredients_key] = full_ingredients
        request.session['title'] = title
        request.session['image'] = image
        request.session['instrs'] = instrs

        # STARTS HERE
        sainsburys_total_price, sainsburys_item_links = 0, []
        asda_total_price, asda_item_links = 0, []
        tesco_total_price, tesco_item_links = 0, []
        morrisons_total_price, morrisons_item_links = 0, [] #tesco_total_price, tesco_item_links 
        cheapest_total_market = ""
        cheapest_found_entries_market = ""
        # ENDS HERE

        show_table = False
        found_row_ingredients = []
        not_found_row_ingredients = []
        asda_found_entries_total_price = 0
        tesco_found_entries_total_price = 0
        sainsburys_found_entries_total_price = 0
        morrisons_found_entries_total_price = 0


    
    ingredients = list(filter(None, list(map(lambda s: s.strip().title(), ingredients))))
    full_ingredients = list(filter(None, list(map(lambda s: s.strip().title(), full_ingredients)))) 
    ingredients_form = IngredientsForm(full_ingredients=full_ingredients, ingredients=ingredients)

    
    context = {
        original_ingredients_key : original_ingredients,
        full_ingredients_key     : full_ingredients,
        'ingredients'            : ingredients,
        'sainsburys_total_price' : sainsburys_total_price,
        'asda_total_price'       : asda_total_price,
        'tesco_total_price'      : tesco_total_price,
        'morrisons_total_price'  : morrisons_total_price,
        'sainsburys_item_links'  : sainsburys_item_links,
        'asda_item_links'        : asda_item_links,
        'tesco_item_links'       : tesco_item_links,
        'morrisons_item_links'   : morrisons_item_links,
        'ingredients_form'       : ingredients_form,
        'recipe_title'           : title,
        'recipe_image'           : image,
        'method'                 : instrs,
        'cheapest_total_market'  : cheapest_total_market,
        'show_table': show_table,
        'found_row_ingredients': found_row_ingredients, 
        'not_found_row_ingredients': not_found_row_ingredients,
        'asda_found_entries_total_price': asda_found_entries_total_price,
        'tesco_found_entries_total_price': tesco_found_entries_total_price,
        'sainsburys_found_entries_total_price': sainsburys_found_entries_total_price,
        'morrisons_found_entries_total_price': morrisons_found_entries_total_price,
        'cheapest_found_entries_market': cheapest_found_entries_market,
        'show_not_found_entries': not_found_row_ingredients != [],
    }
    
    return render(request, "drpapp/comparison.html", context=context)

def diet(request):
    print("diet called")
    if request.method == 'POST':
        form = DietForm(request.POST)
        if form.is_valid():
            # save form data to the database
            print("Form valid:", form)
            instance = form.save()
            request.session['instance_id'] = instance.id
            # redirect to home page (index)
            return redirect('index')

    else:
        instance_id = request.session.get('instance_id')
        instance = DietaryRestriction.objects.filter(id=instance_id).first()
        form = DietForm(instance=instance)

    context = {'form': form }

    return render(request, 'drpapp/diet.html', context)

def proxy_tesco_basket(request):
    print("proxy_tesco_basket called")
    if request.method == 'PUT':
        url = 'https://www.tesco.com/groceries/en-GB/trolley/items?_method=PUT'
        payload = request.body
        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en;q=0.9',
            'path': '/groceries/en-GB/trolley/items?_method=PUT',
            'content-type': 'application/json',
            # 'referer': 'https://www.tesco.com/groceries/en-GB/trolley',
            # 'origin': 'https://www.tesco.com',
        }
        headers.update(request.headers)  # Include any other headers from the original request (CSRF)
        print("Headers from proxy to Tesco:")
        print(headers)
        response = requests.put(url, data=payload, headers=headers)
        
        # Pass the response from Tesco back to the client-side JavaScript
        print("Response from Tesco:", response.json())
        return JsonResponse(response.json())
    else:
        # Handle other HTTP methods if needed
        print("Invalid request method to proxy")
        return JsonResponse({'error': 'Invalid request method'})



def get_tesco_product_links(items):
    # A Tesco link looks like this: https://www.tesco.com/groceries/en-GB/products/<product-id>
    base_url = "https://www.tesco.com/groceries/en-GB/products/"
    for ingredient in items:
        if items[ingredient][0] != "INVALID":
            items[ingredient] = base_url + items[ingredient][0], items[ingredient][1]
    return items

def get_morrisons_product_links(items):
    # A Morrisons link looks like this: https://groceries.morrisons.com/products/<id>
    base_url = "https://groceries.morrisons.com/products/"
    for ingredient in items:
        if items[ingredient][0] != "INVALID":
            items[ingredient] = base_url + items[ingredient][0], items[ingredient][1]
    return items

def get_sainsburys_product_links(items):
    return items

def get_asda_product_links(items):
    # An ASDA link looks like this: https://groceries.asda.com/product/<product-id>
    base_url = "https://groceries.asda.com/product/"
    for ingredient in items:
        if items[ingredient][0] != "INVALID":
            items[ingredient] = base_url + items[ingredient][0], items[ingredient][1]
    return items
   
def money_value(price):
    if str(price)[0].isnumeric():
        val = price
    else:
        # remove the £ sign
        val = price[1:]
    return round(float(val), 2)

def tesco_worker(ingredient, items, preferences, request):
    ingredient_key = "-".join([ingredient, 't'] + ([] if preferences is None else list(filter(lambda k: preferences[k], preferences.keys()))))
    print(ingredient_key)
    if request.session.get(ingredient_key) is None:
        most_relevant_item = searchTesco(ingredient, preferences)
        if most_relevant_item is not None:
            price = most_relevant_item['price']
            price = money_value(price)
            item_id = most_relevant_item['id']
            items[ingredient] = item_id, '£' + f'{price:.2f}'
            request.session[ingredient_key] = item_id, price 
            return price
        else:
            items[ingredient] = "INVALID", "0"
            request.session[ingredient_key] = "INVALID", "0" 
            return 0
    else:
        item_id, price = request.session.get(ingredient_key)
        if item_id == "INVALID":
            items[ingredient] = "INVALID", "0"
            return 0
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price
        
def sainsburys_worker(ingredient, items, preferences, request):
    ingredient_key = "-".join([ingredient, 's'] + ([] if preferences is None else list(filter(lambda k: preferences[k], preferences.keys()))))
    print(ingredient_key)
    if request.session.get(ingredient_key) is None:
        most_relevant_item = searchSainsburys(ingredient, preferences)
        if most_relevant_item is not None:
            price = most_relevant_item['retail_price']['price']
            price = money_value(price)
            items[ingredient] = most_relevant_item['full_url'], '£' + f'{price:.2f}'
            request.session[ingredient_key] = most_relevant_item['full_url'], price 
            return price
        else:
            items[ingredient] = "INVALID", "0"
            request.session[ingredient_key] = "INVALID", "0" 
            return 0
    else:
        full_url, price = request.session.get(ingredient_key)
        if full_url == "INVALID":
            items[ingredient] = "INVALID", "0"
            return 0
        items[ingredient] = full_url, '£' + f'{price:.2f}'
        return price

def asda_worker(ingredient, items, preferences, request):
    ingredient_key = "-".join([ingredient, 'a'] + ([] if preferences is None else list(filter(lambda k: preferences[k], preferences.keys()))))
    print(ingredient_key)
    if request.session.get(ingredient_key) is None:
        most_relevant_item = searchAsda(ingredient, preferences)
        if most_relevant_item is not None:
            # price is a string of the form £<price> (not a string for the tesco api though)
            price_str = most_relevant_item.get('price')
            price = money_value(price_str)
            item_id = most_relevant_item['id']
            items[ingredient] = item_id, '£' + f'{price:.2f}'
            request.session[ingredient_key] = item_id, price 
            return price
        else:
            items[ingredient] = "INVALID", "0"
            request.session[ingredient_key] = "INVALID", "0" 
            return 0 
    else: 
        item_id, price = request.session.get(ingredient_key)
        if item_id == "INVALID":
            items[ingredient] = "INVALID", "0"
            return 0
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price


def morrisons_worker(ingredient, items, preferences, request):
    ingredient_key = "-".join([ingredient, 'm'] + ([] if preferences is None else list(filter(lambda k: preferences[k], preferences.keys()))))
    print(ingredient_key)
    if request.session.get(ingredient_key) is None:
        most_relevant_item = search_morrisons(ingredient, preferences)
        if most_relevant_item is not None:
            price = most_relevant_item['product']['price']['current']
            item_id = most_relevant_item['sku']
            items[ingredient] = item_id, '£' + f'{price:.2f}'
            request.session[ingredient_key] = item_id, price 
            return price
        else:
            items[ingredient] = "INVALID", "0"
            request.session[ingredient_key] = "INVALID", "0" 
            return 0
    else: 
        item_id, price = request.session.get(ingredient_key)
        if item_id == "INVALID":
            items[ingredient] = "INVALID", "0"
            return 0
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price


def total_price_tesco(ingredients, preferences, request):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(tesco_worker, ingredient, items, preferences, request) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    executor.shutdown()
    item_links = get_tesco_product_links(items)

    return total_price, item_links

def total_price_asda(ingredients, preferences, request):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(asda_worker, ingredient, items, preferences, request) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_asda_product_links(items)

    executor.shutdown()

    return total_price, item_links

def total_price_sainsburys(ingredients, preferences, request):
    items = {}
    num_threads = 4
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(sainsburys_worker, ingredient, items, preferences, request) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_sainsburys_product_links(items)

    executor.shutdown()

    return total_price, item_links

def total_price_morrisons(ingredients, preferences, request):
    items = {}
    num_threads = 3
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
    
    results = [executor.submit(morrisons_worker, ingredient, items, preferences, request) for ingredient in ingredients]
    
    concurrent.futures.wait(results)
    
    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_morrisons_product_links(items)
    
    executor.shutdown()
    
    return total_price, item_links

def get_cheapest_market(prices):
    supermarket_names = ["Sainsbury's", "Asda", "Morrisons", "Tesco"] 
    return supermarket_names[prices.index(min(prices))]