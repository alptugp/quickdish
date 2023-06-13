from django.db import models
from django import forms

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