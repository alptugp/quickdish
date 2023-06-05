from timeit import default_timer as timer
from django.shortcuts import render, redirect
from .RecipeParser import get_ingredients
from .TescoWebScraper import getMostRelevantItemTesco
from .AsdaSearch import searchAsda
from .SainsburysSearch import searchSainsburys
from .models import DietForm, DietaryRestriction
import concurrent.futures
import spacy

def index(request):
    return render(request, "drpapp/index.html")

def token_good(token):
    units = ["tbsp", "tsp", "g", "kg", "oz"]
    if not (token.pos_ == "NOUN" or token.pos_ == "ADJ"):
        return False
    if token.text in units:
        return False
    return True

def recommendations(request):
    return render(request, "drpapp/recommendations.html")

def comparison(request): 
    # Get what the user typed in the search bar (the recipe url) after they press the enter button
    query = request.GET.get('query', '')

    instance_id = request.session.get('instance_id')

    ingredients_start_time = timer()
    original_ingredients = get_ingredients(query)
    ingredients_end_time = timer()

    toProcess = []
    for ingredient in original_ingredients:
        nlp = spacy.load("en_core_web_sm")
        if "of" in ingredient:
            toProcess.append(ingredient.split("of")[1])
        else:
            toProcess.append(ingredient)
    
    nlp_start_time = timer()
    processed = list(nlp.pipe(toProcess))
    
    ingredients = []
    for tokens in processed:
        ingredient = ""
        for token in tokens:
            if token.text == "or" or token.text == ",":
                break
            if token_good(token):
                if ingredient:
                    ingredient += " "
                ingredient += token.text
        ingredients.append(ingredient)
    nlp_end_time = timer()

    sains_start_time = timer()
    sainsburys_total_price, sainsburys_item_links = total_price_sainsburys(ingredients)
    sains_end_time = timer()
    asda_start_time = timer()
    asda_total_price, asda_item_links = total_price_asda(ingredients, instance_id)
    asda_end_time = timer()

    ingredients_elapsed = round((ingredients_end_time - ingredients_start_time) * 1000)
    nlp_elapsed = round((nlp_end_time - nlp_start_time) * 1000)
    sains_elapsed = round((sains_end_time - sains_start_time) * 1000)
    asda_elapsed = round((asda_end_time - asda_start_time) * 1000)

    context = {
        'original_ingredients': original_ingredients,
        'ingredients': ingredients,
        'sainsburys_total_price': sainsburys_total_price,
        'asda_total_price': asda_total_price,
        'sainsburys_item_links': sainsburys_item_links,
        'asda_item_links': asda_item_links,
        'ingredients_elapsed': ingredients_elapsed,
        'nlp_elapsed': nlp_elapsed,
        'sains_elapsed': sains_elapsed,
        'asda_elapsed': asda_elapsed
    }
    
    return render(request, "drpapp/comparison.html", context)

def diet(request):
    if request.method == 'POST':
        form = DietForm(request.POST)
        if form.is_valid():
            # save form data to the database
            instance = form.save()  
            request.session['instance_id'] = instance.id
            # redirect to home page (index)
            return redirect('index')

    else:
        instance_id = request.session.get('instance_id')
        instance = DietaryRestriction.objects.filter(id=instance_id).first()
        form = DietForm(instance=instance)

        # initial_data = {
        #     'vegan': request.GET.get('vegan', False), # request.session.get?
        #     'vegetarian': request.GET.get('vegetarian', False),
        #     'gluten_free': request.GET.get('gluten_free', False) 
        # }
        # form = DietForm(initial=initial_data)

    context = {'form': form }

    return render(request, 'drpapp/diet.html', context)

def get_tesco_product_links(items):
    # A Tesco link looks like this: https://www.tesco.com/groceries/en-GB/products/<product-id>
    base_url = "https://www.tesco.com/groceries/en-GB/products/"
    for ingredient in items:
        if items[ingredient] != "INVALID":
            items[ingredient] = base_url + items[ingredient]
    return items

def get_sainsburys_product_links(items):
    return items

def get_asda_product_links(items):
    # An ASDA link looks like this: https://groceries.asda.com/product/<product-id>
    base_url = "https://groceries.asda.com/product/"
    for ingredient in items:
        if items[ingredient] != "INVALID":
            items[ingredient] = base_url + items[ingredient]
    return items
   
def money_value(price):
    if str(price)[0].isnumeric():
        val = price
    else:
        # remove the £ sign
        val = price[1:]
    return round(float(val), 2)

def tesco_worker(ingredient, items, form_instance):
    most_relevant_item = getMostRelevantItemTesco(str(ingredient), form_instance)
    price = most_relevant_item['price']
    price = money_value(price)
    item_id = most_relevant_item['id']
    items[ingredient] = item_id
    return price

def sainsburys_worker(ingredient, items):
    most_relevant_item = searchSainsburys(ingredient)
    if most_relevant_item is not None:
        price = most_relevant_item['retail_price']['price']
        price = money_value(price)
        items[ingredient] = most_relevant_item['full_url']
        return price
    else:
        items[ingredient] = "INVALID"
        return 0

def asda_worker(ingredient, items, form_instance):
    most_relevant_item = searchAsda(ingredient, form_instance)
    if most_relevant_item is not None:
        # price is a string of the form £<price> (not a string for the tesco api though)
        price_str = most_relevant_item.get('price')
        price = money_value(price_str)
        item_id = most_relevant_item['id']
        items[ingredient] = item_id
        return price
    else:
        items[ingredient] = "INVALID"
        return 0 

def total_price_tesco(ingredients, instance_id):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    if instance_id is None:
        form_instance = None
    else:
        form_instance = DietaryRestriction.objects.get(id = instance_id)

    results = [executor.submit(tesco_worker, ingredient, items, form_instance) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0 
    for result in results:
        total_price += result.result()
    
    

    executor.shutdown()
    item_links = get_tesco_product_links(items)

    return total_price, item_links

def total_price_asda(ingredients, instance_id):
    items = {}
    num_threads = 2
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    if instance_id is None:
        form_instance = None
    else:
        form_instance = DietaryRestriction.objects.get(id = instance_id)

    results = [executor.submit(asda_worker, ingredient, items, form_instance) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = money_value(total_price)
    
    item_links = get_asda_product_links(items)

    executor.shutdown()

    return total_price, item_links

def total_price_sainsburys(ingredients):
    items = {}
    num_threads = 3
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    results = [executor.submit(sainsburys_worker, ingredient, items) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = money_value(total_price)
    
    item_links = get_sainsburys_product_links(items)

    executor.shutdown()

    return total_price, item_links
