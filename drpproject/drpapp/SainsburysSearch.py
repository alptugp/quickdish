import requests
from .NLP import *

# Sample GET request for "egg" search
# https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=egg&page_number=1&page_size=5&sort_order=FAVOURITES_FIRST

def constructSainsburysGetRequest(item, preferences):
    # # TODO: Fix searching with dietary preferences
    # if preferences:
    #     for pref in preferences.keys():
    #         if preferences.get(pref):
    #             item = pref + item
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

def searchSainsburys(item, preferences):
    request = constructSainsburysGetRequest(item, preferences)
    response = requests.get(request)

    try:
        return response.json().get('products')[0]
    except:
        categories = ["ADJ"]
        item_retry = strip_words(item, categories=categories)
        if item != item_retry:
            retry = searchSainsburys(item_retry, preferences)
            if retry:
                print(f"SAINSBURYS: Cannot find \"{item}\", but found \"{item_retry}\"")
                return retry
            else:
                print(f"SAINSBURYS: Cannot find \"{item}\"")
        else:
            return None