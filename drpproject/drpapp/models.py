from django.db import models
from django import forms

class SavedRecipe(models.Model):
    recipe_name = models.CharField(max_length=100)
    recipe_url = models.CharField(max_length=255)
    ingredients = models.JSONField()

    def __init__(self, recipe_name, recipe_url, ingredients, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipe_name = str(recipe_name).strip()
        self.recipe_url = str(recipe_url).strip()
        self.ingredients = ingredients

class SavedShoppingList(models.Model):
    saved_recipes = models.ManyToManyField(SavedRecipe)

class DietaryRestriction(models.Model):
    vegan = models.BooleanField(default = False)
    vegetarian = models.BooleanField(default = False)
    gluten_free = models.BooleanField(default = False)

class DietForm(forms.ModelForm):
    class Meta:
        model = DietaryRestriction
        fields = ["vegan", "vegetarian", "gluten_free"]

class IngredientsForm(forms.Form):
    new_ingredient = forms.CharField(
        label = 'add_ingredient',
        required = False,
        widget = forms.TextInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Add an ingredient',
            }
        )
    )
    def __init__(self, full_ingredients, ingredients, *args, **kwargs):
        super(IngredientsForm, self).__init__(*args, **kwargs)
        for ingredient in full_ingredients:
            if ingredient != "csrfmiddlewaretoken":
                field_name = ingredient
                wanted = ingredient in ingredients
                self.fields[field_name] = forms.BooleanField(
                    label=ingredient, 
                    initial=wanted, 
                    required=False,
                    widget=forms.CheckboxInput()
                )

# For tracking dead clicks. 
class DeadClick(models.Model):
    # All fields are optional, as we may not be able to get all the information (?)
    
    # timestamp of the click
    timestamp = models.DateTimeField(null=True) #auto_now_add=True ?
    
    # url of the page where the click occurred
    url = models.URLField(null=True)
    
    # x and y coordinates of the click
    x = models.IntegerField(null=True)
    y = models.IntegerField(null=True)
    
    # DOM element information of the where the click occurred
    tag_name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    element_id = models.CharField(max_length=255, null=True)