from recipe_scrapers import scrape_me

def get_ingredients(url):
    scraper = scrape_me(url)
    return scraper.ingredients()