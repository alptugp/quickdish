import re
import nltk
from ingredient_parser import parse_multiple_ingredients

nltk.download('averaged_perceptron_tagger')

units = ["teaspoon", "tablespoon",
         "tsp", "tbsp",
         "cup", "pack", "tub", "bag", "jar", "piece", "each", "ea",
         "pint", "gallon", "quart",
         "gram", "kilogram", "pound", "ounce",
         "g", "kg", "lb", "lb",
         "cm", "m", "inch",
         "pt", "gal", "qt", "oz", "ml", "l", "L",
         "1/2", "1/4", "½", "¼",
         "handful", "large handful"]

def remove_empty_strings(words):
    return [word for word in words if word and word.strip()]

def remove_bracketed_text(original):
    pattern = r'\([^)]*\)'
    modified_string = re.sub(pattern, '', original)
    return modified_string.strip()

def unit_list_to_regex(strings):
    disj = "|".join(re.escape(string) for string in strings)
    disj += "s?"
    return f"({disj})"

def remove_units(original):
    unit_pattern = unit_list_to_regex(units)
    pattern = fr'\b\d+(\.\d+)?\s*{unit_pattern}\b'
    modified_string = re.sub(pattern, '', original)
    return modified_string.strip()

def split_3_a_comma_b_and_c(original):
    pattern = r"([\w\s]*?)\s*,\s*([\w\s]+?)((\s+)|(\s*,\s*))and\s+([\w\s]+)"
    match = re.match(pattern, original)
    if match:
        split = match.groups()
        return remove_empty_strings(split)
    else:
        return [original]

def splitAndGetUseful(original):
    toProcess = []
    original = remove_bracketed_text(original)
    temps = split_3_a_comma_b_and_c(original)

    for temp in temps:
        if " or " in temp:
            temp = temp.split(" or ")[1]
        if " such as " in temp:
            temp = temp.split(" such as ")[1]
        if " like " in temp:
            temp = temp.split(" like ")[1]
        # if "sized " in temp:
        #     temp = temp.split("sized ")[1]
        if " and " in temp:
            [l, r] = [remove_units(x) for x in temp.split(" and ", 1)]
            toProcess.append(l)
            toProcess.append(r)
        else:
            temp = remove_units(temp)
            toProcess.append(temp)
    return toProcess

def cleanup_ingredients(original_ingredients):
    to_process = []

    # Step 1: Convert to lowercase
    original_ingredients = [ingredient.lower() for ingredient in original_ingredients]
    
    # Step 2: Remove bracketed text, split multiple, remove units
    for ingredient in original_ingredients:
        temps = splitAndGetUseful(ingredient)
        to_process.extend(temps)
    
    # Step 3: Extract ingredient name using NLP library
    property = 'name'
    parsed = parse_multiple_ingredients(to_process)

    for ingredient in parsed:
        print(f"{ingredient['name']}\nComment: {ingredient['comment']}\nOther: {ingredient['other']}\n")

    ingredients = [ingredient[property] for ingredient in parsed]
    
    # Step 3: Remove empty strings
    ingredients = remove_empty_strings(ingredients)

    # Step 4: Remove duplicate ingredients
    ingredients = set(ingredient.lower() for ingredient in ingredients)

    return list(ingredients)