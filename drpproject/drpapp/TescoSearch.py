import requests
from bs4 import BeautifulSoup

def constructTescoGetRequest(item, diet_preferences):
    if diet_preferences is not None:
        if diet_preferences.vegan:
            item = "vegan " + item
        if diet_preferences.vegetarian:
            item = "vegetarian " + item
        if diet_preferences.gluten_free:
            item = "gluten-free " + item
    params = {
        "q" : item
    }
    url = "https://www.tesco.com/search/?"
    paramString = [(param + "=" + val) for (param, val) in params.items()]
    delim = "&"
    url += delim.join(paramString)
    return url

def searchTesco(item, form_instance):
    request = constructTescoGetRequest(item, form_instance)
    response = requests.get(request)

    print(f"{response.text}\nGOT HERE\n")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first search result item
    first_result = soup.find('div', {'class': 'product-list--list-item'})

    # Extract information from the search result item
    product_name = first_result.find('a', {'class': 'sc-kjoXOD'}).text
    product_price = first_result.find('span', {'class': 'value'}).text
    product_id = "some id"

    result = {
        'name' : product_name,
        'price' : product_price,
        'id' : product_id,
    }

    # Print the extracted information
    print(f"Product Name: {product_name}")
    print(f"Product Price: {product_price}")
    print(f"Product ID: {product_id}")

    try:
        return result
    except:
      print(f"Cannot find {item} in Tesco")
      return None