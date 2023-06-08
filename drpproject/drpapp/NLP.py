import re
import spacy

nlp = spacy.load("en_core_web_sm")

def strip_words(original, categories):
    tokens = nlp(original)
    processed = ""
    for token in tokens:
        if token.pos_ not in categories:
            if processed:
                processed += " "
            processed += token.text
    return processed

def token_good(token):
    units = ["tbsp", "tsp",
             "g", "kg",
             "oz", "ml", "l",
             "pack", "tub", "bag", "jar",
             "1/2", "1/4", "½",
             "handful", "large handful"]
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
    return modified_string

def cleanupIngredients(original_ingredients):
    toProcess = []

    for ingredient in original_ingredients:
        # Example: 500g of (soft) butter => 500g of butter
        temp = remove_bracketed_text(ingredient)
        
        # Example: 500g of butter => butter
        if " of " in temp:
            temp = temp.split(" of ")[1]
            # toProcess.append(temp.split(" of ")[1])
        if "," in temp:
            temp = temp.rsplit(",", 1)[0]
        if " or " in temp:
            temp = temp.split(" or ")[1]
        if " and " in temp:
            [l, r] = temp.split(" and ", 1)
            toProcess.append(l)
            toProcess.append(r)
        else:
            toProcess.append(temp)
    
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

    return list(set(ingredient.lower() for ingredient in ingredients))