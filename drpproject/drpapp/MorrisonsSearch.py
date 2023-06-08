import requests
from .NLP import *

# Sample GET request for "milk" search with vegan, vegetarian, gluten free tags
# https://groceries.morrisons.com/webshop/api/v1/search?hideOOS=true&searchTerm=milk&tags=19993,19996,20011
# https://groceries.morrisons.com/webshop/api/v1/search?hideOOS=true&searchTerm=blue%20milk&tags=20011
        
def construct_morrisons_get_request(item, preferences):
    pref_tags = {
        "vegan": "20011",
        "vegetarian": "19996",
        "gluten_free": "19993",
    }
    tags = []
    if preferences:
        for pref in preferences.keys():
            if preferences.get(pref):
                tags.append(pref_tags.get(pref))
    
    if len(tags) > 0:
        tags = ",".join(tags)
    else:
        tags = ""
    
    params = {
        "hideOOS" : "true",
        "searchTerm" : item,
        "tags" : tags,
    }
    url = "https://groceries.morrisons.com/webshop/api/v1/search?"
    paramString = [(param + "=" + val) for (param, val) in params.items()]
    delim = "&"
    url += delim.join(paramString)
    return url

def search_morrisons(item, preferences):
    request = construct_morrisons_get_request(item, preferences)
    response = requests.get(request)

    try:
        return response.json().get('mainFopCollection')['sections'][0]['fops'][0]
    except:
        categories = ["ADJ"]
        item_retry = strip_words(item, categories=categories)
        if item != item_retry:
            retry = search_morrisons(item_retry, preferences)
            if retry:
                print(f"MORRISONS: Cannot find \"{item}\", but found \"{item_retry}\"")
                return retry
            else:
                print(f"MORRISONS: Cannot find \"{item}\"")
        else:
            return None