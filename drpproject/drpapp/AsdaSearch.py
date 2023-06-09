import requests
from .NLP import *

# Sample GET request for "egg" search
# https://groceries.asda.com/p13nservice/recommendations?storeId=4565&shipDate=currentDate&amendFlag=false&limit=2&placement=search_page.search1_mab&searchTerm=egg&searchQuery=egg&includeSponsoredProducts=false&pageType=SEARCH

def constructAsdaGetRequest(item, preferences):
    # # TODO: Fix searching with dietary preferences
    # if preferences:
    #     for pref in preferences.keys():
    #         if preferences.get(pref):
    #             item = pref + item
    params = {
        "storeId" : "4565",
        "shipDate" : "currentDate",
        "amendFlag" : "false",
        "limit" : "2",
        "placement" : "search_page.search1_mab",
        "searchTerm" : item,
        "searchQuery" : item,
        "includeSponsoredProducts" : "false",
        "pageType" : "SEARCH",
    }
    url = "https://groceries.asda.com/p13nservice/recommendations?"
    paramString = [(param + "=" + val) for (param, val) in params.items()]
    delim = "&"
    url += delim.join(paramString)
    return url

def searchAsda(item, preferences):
    request = constructAsdaGetRequest(item, preferences)
    response = requests.get(request)
    
    attempts = 3
    for _ in range(attempts):
        try:
            return response.json().get('results')[0].get('items')[0]
        except:
            categories = ["ADJ"]
            item_retry = strip_words(item, categories=categories)
            if item != item_retry:
                retry = searchAsda(item_retry, preferences)
                if retry:
                    print(f"ASDA: Cannot find \"{item}\", but found \"{item_retry}\"")
                    return retry
                else:
                    print(f"ASDA: Cannot find \"{item}\"")
            else:
                return None