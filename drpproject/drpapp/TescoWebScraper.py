from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_dqzb5ZnhW0iNL7DRoC43yl86ucC9KE3fq6fu")


def getMostRelevantItemTesco(query, diet_preferences):
    dietaries = []
    # iterate through the diet preferences, if true, add to the list
    for diet in diet_preferences:
        if diet.vegan:
            dietaries.append("Vegan")
        if diet.vegetarian:
            dietaries.append("Vegetarian")
        if diet.gluten_free:
            dietaries.append("No gluten")

    # Prepare actor input
    run_input = { "query":  query, "sort": "relevance", "limit": 1, "dietaries": dietaries }

    # Run the actor and wait for it to finish
    run = client.actor("jupri/tesco-grocery").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        return item





