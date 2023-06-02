from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_dqzb5ZnhW0iNL7DRoC43yl86ucC9KE3fq6fu")

def getMostRelevantItemAsda(query):
    if query == "milk": 
        return {'price': {'price_info': {'price': "£0.90"}}, 'item': {'sku_id':  "37518"}} 
    if query == "eggs": 
        return {'price': {'price_info': {'price': "£2.50"}}, 'item': {'sku_id':  "910000045549"}} 
    if query == "sunflower oil": 
        return {'price': {'price_info': {'price': "£2.40"}}, 'item': {'sku_id':  "47279876"}} 
    if query == "butter": 
        return {'price': {'price_info': {'price': "£1.75"}}, 'item': {'sku_id':  "1000383135604"}} 
    if query == "sugar": 
        return {'price': {'price_info': {'price': "£0.89"}}, 'item': {'sku_id':  "21051"}}
    # Prepare the actor input
    run_input = { "keywords": query, "limit": 1 }

    # Run the actor and wait for it to finish
    run = client.actor("jupri/asda-scraper").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    items = client.dataset(run["defaultDatasetId"]).iterate_items()
    try:
        return next(items)
    except StopIteration:
        return None






