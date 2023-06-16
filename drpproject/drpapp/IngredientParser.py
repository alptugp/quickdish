import os
import certifi
import re
import spacy
import nltk
from ingredient_parser import parse_multiple_ingredients

os.environ["SSL_CERT_FILE"] = certifi.where()
nltk.download('averaged_perceptron_tagger')

nlp = spacy.load("en_core_web_sm")

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
    number_pattern = '(\d+(\.\d+)?|½|¼)'
    unit_pattern = unit_list_to_regex(units)
    pattern = fr'\b{number_pattern}(\s*-\s*{number_pattern})?\s*{unit_pattern}\b'
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

def contains_nouns(original):
    tokens = nlp(original)
    for token in tokens:
        if token.pos_ == "NOUN":
            return True
    return False

def splitAndGetUseful(original):
    toProcess = []
    original = remove_bracketed_text(original)
    temps = split_3_a_comma_b_and_c(original)

    for temp in temps:
        if not contains_nouns(temp):
            temps = [original]
            break

    for temp in temps:
        if " of " in temp:
            temp = temp.split(" of ")[1]
        if " or " in temp:
            temp = temp.split(" or ")[1]
        if " such as " in temp:
            temp = temp.split(" such as ")[1]
        if " like " in temp:
            temp = temp.split(" like ")[1]
        temp = remove_units(temp)
        toProcess.append(temp)
    return toProcess

def cleanup_ingredients(original_ingredients):
    to_process = []
    
    # Step 1: Remove bracketed text, split multiple, remove units
    for ingredient in original_ingredients:
        temps = splitAndGetUseful(ingredient)
        to_process.extend(temps)
    
    # Step 2: Extract ingredient name using NLP library
    property = 'name'
    parsed = parse_multiple_ingredients(to_process)

    ingredients = [ingredient[property] for ingredient in parsed]
    
    # Step 3: Remove units
    ingredients = remove_empty_strings(ingredients)

    # Step 4: Remove empty strings
    ingredients = [remove_units(ingredient) for ingredient in ingredients]

    # Step 5: Remove duplicates and convert to lowercase
    ingredients = set(ingredient.lower() for ingredient in ingredients)

    return list(ingredients)