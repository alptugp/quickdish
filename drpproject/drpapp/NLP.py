import re
import spacy

nlp = spacy.load("en_core_web_sm")

units = ["teaspoon", "tablespoon",
         "tsp", "tbsp",
         "cup", "pack", "tub", "bag", "jar", "piece",
         "pint", "gallon", "quart",
         "gram", "kilogram", "pound", "ounce",
         "g", "kg", "lb", "lb",
         "cm", "m",
         "pt", "gal", "qt", "oz", "ml", "l", "L",
         "1/2", "1/4", "½",
         "handful", "large handful"]

def strip_words(original, categories):
    tokens = nlp(original)
    processed = ""
    for token in tokens:
        if token.pos_ not in categories:
            if processed:
                processed += " "
            processed += token.text
    return processed

def remove_empty_strings(words):
    return [word for word in words if word and word.strip()]

def token_good(token):
    if not (token.pos_ == "NOUN" or token.pos_ == "ADJ" or token.pos_ == "PROPN"):
        return False
    if token.text in units:
        return False
    if token.text[0].isdigit():
        return False
    return True

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
        print(temp)
        if " of " in temp:
            temp = temp.split(" of ")[1]
        if "," in temp:
            temp = temp.rsplit(",", 1)[0]
        if " or " in temp:
            temp = temp.split(" or ")[1]
        if " such as " in temp:
            temp = temp.split(" such as ")[1]
        if " like " in temp:
            temp = temp.split(" like ")[1]
        if "sized " in temp:
            temp = temp.split("sized ")[1]
        if " and " in temp:
            [l, r] = [remove_units(x) for x in temp.split(" and ", 1)]
            toProcess.append(l)
            toProcess.append(r)
        else:
            temp = remove_units(temp)
            toProcess.append(temp)
    return toProcess

def cleanupIngredients(original_ingredients):
    toProcess = []

    for ingredient in original_ingredients:
        temps = splitAndGetUseful(ingredient)
        toProcess.extend(temps)
    
    processed = list(nlp.pipe(toProcess))
    
    ingredients = []
    for tokens in processed:
        ingredient = ""
        for token in tokens:
            if token_good(token):
                if ingredient:
                    ingredient += " "
                ingredient += token.text
        ingredients.append(ingredient)
    
    ingredients = remove_empty_strings(ingredients)

    return list(set(ingredient.lower() for ingredient in ingredients))