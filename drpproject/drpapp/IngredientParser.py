from ingredient_parser import parse_ingredient

def get_ingredient_name(ingredient):
    return get_ingredient_by_symbol(ingredient, property='name')

def get_ingredient_by_symbol(ingredient, property):
    parsed = parse_ingredient(ingredient)
    return parsed.get(ingredient, property)

def cleanup_ingredients(original_ingredients):
    property = 'name'
    ingredients = [get_ingredient_name(ingredient) for ingredient in original_ingredients]
    return ingredients