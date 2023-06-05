from timeit import default_timer as timer
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .RecipeParser import get_ingredients
from .TescoWebScraper import getMostRelevantItemTesco
from .AsdaSearch import searchAsda
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

def comparison(request): 
    # Get what the user typed in the search bar (the recipe url) after they press the enter button
    query = request.GET.get('query', '')

    instance_id = request.session.get('instance_id')
    # print("HERE LIES THE INSTANCE ID IDIDIDIDIDIDIDID ID DI DI DID ID ID DI ")
    # print(instance_id)

    ingredientsOriginal = get_ingredients(query)

    toProcess = []
    for ingredient in ingredientsOriginal:
        nlp = spacy.load("en_core_web_sm")
        if "of" in ingredient:
            toProcess.append(ingredient.split("of")[1])
        else:
            toProcess.append(ingredient)
    start = timer()
    processed = list(nlp.pipe(toProcess))
    elapsed = timer() - start
    
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

    # print("Original ingredients: " + str(ingredientsOriginal) + "\n")
    # print("NLP-cleaned ingredients:" + str(ingredients) + "\n")
    # print("\nNLP took " + str(elapsed * 1000) + "ms\n")

    tesco_total_price, tesco_item_links = total_price_tesco(ingredients, instance_id)
    asda_total_price, asda_item_links = total_price_asda(ingredients)

    context = {
        'original_ingredients': ingredientsOriginal,
        'ingredients': ingredients,
        'tesco_total_price': tesco_total_price,
        'asda_total_price': asda_total_price,
        'tesco_item_links': tesco_item_links,
        'asda_item_links': asda_item_links
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
        items[ingredient] = base_url + items[ingredient]
    return items

def get_asda_product_links(items):
    # An ASDA link looks like this: https://groceries.asda.com/product/<product-id>
    base_url = "https://groceries.asda.com/product/"
    for ingredient in items:
        items[ingredient] = base_url + items[ingredient]
    return items
   

def tesco_worker(ingredient, items, form_instance):
    most_relevant_item = getMostRelevantItemTesco(str(ingredient), form_instance)
    price = most_relevant_item['price']
    price = round(float(price), 2)
    item_id = most_relevant_item['id']
    items[ingredient] = item_id
    return price

def asda_worker(ingredient, items):
    most_relevant_item = searchAsda(str(ingredient))
    if most_relevant_item is not None:
        # price is a string of the form £<price> (not a string for the tesco api though)
        price_str = most_relevant_item.get('price')
        # remove the £ sign and convert to float (2dp)
        price = round(float(price_str[1:]), 2)
        item_id = most_relevant_item.get('id')
        items[ingredient] = item_id
        return price
    else:
        # TODO: fix this 
        items[ingredient] = '0'
        return 0 

def total_price_tesco(ingredients, instance_id):
    items = {}
    num_threads = 5
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
    # print("INSTANCE ID", instance_id)
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



