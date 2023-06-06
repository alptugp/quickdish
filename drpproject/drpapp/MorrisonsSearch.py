import requests

# Sample GET request for "milk" search with vegan, vegetarian, gluten free tags
# https://groceries.morrisons.com/webshop/api/v1/search?hideOOS=true&searchTerm=milk&tags=19993,19996,20011
# https://groceries.morrisons.com/webshop/api/v1/search?hideOOS=true&searchTerm=blue%20milk&tags=20011
        
def construct_morrisons_get_request(item, diet_preferences):
    vegan_tag = "20011"
    gluten_free_tag = "19993"
    vegetarian_tag = "19996"
    tags = []
    if diet_preferences is not None:
        if diet_preferences.vegan:
            tags.append(vegan_tag)
        if diet_preferences.vegetarian:
            tags.append(vegetarian_tag)
        if diet_preferences.gluten_free:
            tags.append(gluten_free_tag)
    
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

def search_morrisons(item, form_instance):
    request = construct_morrisons_get_request(item, form_instance)
    response = requests.get(request)

    try:
        return response.json().get('mainFopCollection')['sections'][0]['fops'][0] # ['sku'], ['product']['price']['current']
    except:
        print(f"Cannot find {item} in morrisons")
        
