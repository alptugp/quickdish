from django.shortcuts import render, redirect
from .RecipeParser import get_recipe_details
from .TescoSearch import searchTesco
from .AsdaSearch import searchAsda
from .SainsburysSearch import searchSainsburys
from .MorrisonsSearch import search_morrisons
from .NLP import *
from .models import DietForm, DietaryRestriction, IngredientsForm
import concurrent.futures

def index(request):
    return render(request, "drpapp/index.html")

def recommendations(request):
    return render(request, "drpapp/recommendations.html")

def comparison(request):
    instance_id = request.session.get('instance_id')

    original_ingredients_key = 'original_ingredients'
    full_ingredients_key = 'full_ingredients'
    original_ingredients = []
    full_ingredients = []
    ingredients = []

    if request.method == 'POST':
        original_ingredients = request.session.get(original_ingredients_key, [])
        full_ingredients = request.session.get(full_ingredients_key, [])
        for key in request.POST.keys():
            if key != "csrfmiddlewaretoken":
                ingredients.append(key)

    elif request.method == 'GET':
        # Get what the user typed in the search bar (the recipe url) after they press the enter button
        query = request.GET.get('query', '')

        original_ingredients, title, image, instrs = get_recipe_details(query)
        full_ingredients = cleanupIngredients(original_ingredients)
        ingredients = full_ingredients
        request.session[original_ingredients_key] = original_ingredients
        request.session[full_ingredients_key] = full_ingredients
    
    ingredients = list(map(str.title, ingredients))
    full_ingredients = list(map(str.title, full_ingredients)) 
    ingredients_form = IngredientsForm(full_ingredients=full_ingredients, ingredients=ingredients)

    supermarket_functions = [
        total_price_sainsburys,
        total_price_asda,
        total_price_tesco,
        # total_price_morrisons,
    ]
    num_threads = len(supermarket_functions)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
    results = [executor.submit(fun, ingredients, instance_id) for fun in supermarket_functions]
    concurrent.futures.wait(results)
    
    sainsburys_total_price, sainsburys_item_links = results[0].result()
    asda_total_price, asda_item_links = results[1].result()
    tesco_total_price, tesco_item_links = results[2].result()
    morrisons_total_price, morrisons_item_links = tesco_total_price, tesco_item_links #REPLACE THIS
    executor.shutdown()

    print("ITEMSSSSS:", [sainsburys_total_price, asda_total_price, 
                                                         morrisons_total_price, tesco_total_price])

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
        'method'                 : instrs
    }
    
    return render(request, "drpapp/comparison.html", context)

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

def tesco_worker(ingredient, items, form_instance):
    most_relevant_item = searchTesco(ingredient, form_instance)
    if most_relevant_item is not None:
        price = most_relevant_item['price']
        price = money_value(price)
        item_id = most_relevant_item['id']
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price
    else:
        items[ingredient] = "INVALID", "0"
        return 0

def sainsburys_worker(ingredient, items, form_instance):
    most_relevant_item = searchSainsburys(ingredient, form_instance)
    if most_relevant_item is not None:
        price = most_relevant_item['retail_price']['price']
        price = money_value(price)
        items[ingredient] = most_relevant_item['full_url'], '£' + f'{price:.2f}'
        return price
    else:
        items[ingredient] = "INVALID", "0"
        return 0

def asda_worker(ingredient, items, form_instance):
    most_relevant_item = searchAsda(ingredient, form_instance)
    if most_relevant_item is not None:
        # price is a string of the form £<price> (not a string for the tesco api though)
        price_str = most_relevant_item.get('price')
        price = money_value(price_str)
        item_id = most_relevant_item['id']
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price
    else:
        items[ingredient] = "INVALID", "0"
        return 0 

def morrisons_worker(ingredient, items, form_instance):
    most_relevant_item = search_morrisons(ingredient, form_instance)
    if most_relevant_item is not None:
        price = most_relevant_item['product']['price']['current']
        item_id = most_relevant_item['sku']
        items[ingredient] = item_id, '£' + f'{price:.2f}'
        return price
    else:
        items[ingredient] = "INVALID", "0"
        return 0
        

def total_price_tesco(ingredients, instance_id):
    items = {}
    num_threads = 2
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
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    executor.shutdown()
    item_links = get_tesco_product_links(items)

    return total_price, item_links

def total_price_asda(ingredients, instance_id):
    items = {}
    num_threads = 10
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
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_asda_product_links(items)

    executor.shutdown()

    return total_price, item_links

def total_price_sainsburys(ingredients, instance_id):
    items = {}
    num_threads = 10
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)

    if instance_id is None:
        form_instance = None
    else:
        form_instance = DietaryRestriction.objects.get(id = instance_id)

    results = [executor.submit(sainsburys_worker, ingredient, items, form_instance) for ingredient in ingredients]

    concurrent.futures.wait(results)

    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_sainsburys_product_links(items)

    executor.shutdown()

    return total_price, item_links

def total_price_morrisons(ingredients, instance_id):
    items = {}
    num_threads = 3
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
    
    if instance_id is None:
        form_instance = None
    else: 
        form_instance = DietaryRestriction.objects.get(id = instance_id)
    
    results = [executor.submit(morrisons_worker, ingredient, items, form_instance) for ingredient in ingredients]
    
    concurrent.futures.wait(results)
    
    total_price = 0
    for result in results:
        total_price += result.result()
    
    total_price = "{:.2f}".format(money_value(total_price))
    
    item_links = get_morrisons_product_links(items)
    
    executor.shutdown()
    
    return total_price, item_links

def get_cheapest_market(prices):
    market_names = ["Sainsbury's", "Asda", "Morrisons", "Tesco"] 
    return market_names[prices.index(min(prices))]