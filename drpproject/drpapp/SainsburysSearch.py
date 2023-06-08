import requests
from .NLP import *

# Sample GET request for "egg" search
# https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=egg&page_number=1&page_size=5&sort_order=FAVOURITES_FIRST

def constructSainsburysGetRequest(item, diet_preferences):
    if diet_preferences is not None:
        if diet_preferences.vegan:
            item = "vegan " + item
        if diet_preferences.vegetarian:
            item = "vegetarian " + item
        if diet_preferences.gluten_free:
            item = "gluten-free " + item
    params = {
        "page_number" : "1",
        "page_size" : "1",
        "filter[keyword]" : item,
        "sort_order" : "FAVOURITES_FIRST"
    }
    url = "https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?"
    paramString = [(param + "=" + val) for (param, val) in params.items()]
    delim = "&"
    url += delim.join(paramString)
    return url

def searchSainsburys(item, form_instance):
    request = constructSainsburysGetRequest(item, form_instance)
    response = requests.get(request)

    try:
        return response.json().get('products')[0]
    except:
        categories = ["ADJ"]
        item_retry = strip_words(item, categories=categories)
        if item != item_retry:
            retry = searchSainsburys(item_retry, form_instance)
            if retry:
                print(f"SAINSBURYS: Cannot find \"{item}\", but found \"{item_retry}\"")
                return retry
            else:
                print(f"SAINSBURYS: Cannot find \"{item}\"")
        else:
            return None