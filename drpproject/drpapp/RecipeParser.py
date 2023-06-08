from recipe_scrapers import scrape_me

def get_recipe_details(url):
    scraper = scrape_me(url)
    return scraper.ingredients(), scraper.title(), scraper.image(), scraper.instructions_list()
