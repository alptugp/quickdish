import nltk
from ingredient_parser import parse_multiple_ingredients

nltk.download('averaged_perceptron_tagger')

def cleanup_ingredients(original_ingredients):
    property = 'name'
    parsed = parse_multiple_ingredients(original_ingredients)
    ingredients = [ingredient[property] for ingredient in parsed]
    return ingredients