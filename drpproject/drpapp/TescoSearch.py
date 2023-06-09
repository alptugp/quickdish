import requests
import json
from bs4 import BeautifulSoup
from .NLP import *

def constructTescoGetRequest(item, preferences):
    # # TODO: Fix searching with dietary preferences
    # if preferences:
    #     for pref in preferences.keys():
    #         if preferences.get(pref):
    #             item = pref + item
    params = {
        "query" : item,
        # "icid" : f"tescohp_sws-1_m-ft_in-{item}_out-{item}"
    }
    url = "https://www.tesco.com/groceries/en-GB/search?"
    paramString = [(param + "=" + val) for (param, val) in params.items()]
    delim = "&"
    url += delim.join(paramString)

    headers = {
        'User-Agent' : 'Mozilla/5.0',
    }
    return url, headers

def searchTesco(item, preferences):
    request, headers = constructTescoGetRequest(item, preferences)

    # Tesco-specific class names
    script_type = 'application/ld+json'
    item_list_elem_key = 'itemListElement'
    first_page_key = 'list-page-1'
    first_list_item_key = 'product-list--list-item first'
    product_name_element_key = 'styled__Text-sc-1xbujuz-1 ldbwMG beans-link__text'
    product_price_element_key = 'styled__StyledHeading-sc-119w3hf-2 jWPEtj styled__Text-sc-8qlq5b-1 lnaeiZ beans-price__text'
    
    try:
        response = requests.get(request, headers=headers)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first search result item
        item_list = json.loads(soup.find('script', {'type': script_type})
                               .contents[0])[2][item_list_elem_key]
        product_url = item_list[0]['url']
        product_id = product_url.rsplit('/', 1)[-1]
        first_page = soup.find('div', {'class': first_page_key})
        first_list_item = first_page.find('li', {'class': first_list_item_key})
        
        product_name_element = first_list_item.find('span', {'class': product_name_element_key})
        product_name = product_name_element.contents[0]
        product_price_element = first_list_item.find('p', {'class': product_price_element_key})
        product_price = product_price_element.contents[0]

        result = {
            'name' : product_name,
            'price' : product_price,
            'id' : product_id,
            'url' : product_url,
        }

        return result
    
    except:
        categories = ["ADJ"]
        item_retry = strip_words(item, categories=categories)
        if item != item_retry:
            retry = searchTesco(item_retry, preferences)
            if retry:
                print(f"TESCO: Cannot find \"{item}\", but found \"{item_retry}\"")
                return retry
            else:
                print(f"TESCO: Cannot find \"{item}\"")
        else:
            return None