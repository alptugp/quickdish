import requests
import json

# Sample GET request for "egg" search
# https://groceries.asda.com/p13nservice/recommendations?storeId=4565&shipDate=currentDate&amendFlag=false&limit=2&placement=search_page.search1_mab&searchTerm=egg&searchQuery=egg&includeSponsoredProducts=false&pageType=SEARCH

def constructAsdaGetRequest(item):
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

def searchAsda(item):
    request = constructAsdaGetRequest(item)
    response = requests.get(request)

    try:
        return response.json().get('results')[0].get('items')[0]
    except:
        print(f"Cannot find {item} in Asda")