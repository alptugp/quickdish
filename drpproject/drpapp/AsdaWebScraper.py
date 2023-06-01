from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_dqzb5ZnhW0iNL7DRoC43yl86ucC9KE3fq6fu")

def getMostRelevantItemAsda(query):
    # Prepare the actor input
    run_input = { "keywords": query, "limit": 1 }

    # Run the actor and wait for it to finish
    run = client.actor("jupri/asda-scraper").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        return item






