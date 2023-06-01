from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_dqzb5ZnhW0iNL7DRoC43yl86ucC9KE3fq6fu")


def getMostRelevantItemTesco(query, diet_preferences):
    dietaries = []
    # Check each preference, if true, add to the list
    if diet_preferences.vegan:
        dietaries.append("Vegan")
    if diet_preferences.vegetarian:
        dietaries.append("Vegetarian")
    if diet_preferences.gluten_free:
        dietaries.append("No gluten")

    # Take head of list for now - api call doesn't allow multiple options. 
    if dietaries != []:
        dietaries = dietaries[0]

    # Prepare actor input
    run_input = { "query":  query, "sort": "relevance", "limit": 1, "dietaries": dietaries }

    # Run the actor and wait for it to finish
    run = client.actor("jupri/tesco-grocery").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    items = client.dataset(run["defaultDatasetId"]).iterate_items()
    try:
        return next(items)
    except StopIteration:
        return None





