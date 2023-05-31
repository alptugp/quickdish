from recipe_scrapers import scrape_me

def get_ingredients(url):
    scraper = scrape_me(url)
    return scraper.ingredients()

"""print(get_ingredients("https://www.bbcgoodfood.com/recipes/lemon-layer-cake-with-soft-cheese-icing"))"""