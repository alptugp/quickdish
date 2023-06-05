import requests
import json

def constructSainsburysGetRequest(item):
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

def searchSainsburys(item):
    request = constructSainsburysGetRequest(item)
    response = requests.get(request)
    
    try:
        return response.json().get('products')[0]
    except:
        print(f"Cannot find {item} in Sainsbury's")
# Sample GET request for "egg" search
# https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=egg&page_number=1&page_size=5&sort_order=FAVOURITES_FIRST