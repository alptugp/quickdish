from django.db import models
from django.forms import Form, ModelForm, BooleanField, CharField, HiddenInput
from django import forms

class DietaryRestriction(models.Model):
    vegan = models.BooleanField(default = False)
    vegetarian = models.BooleanField(default = False)
    gluten_free = models.BooleanField(default = False)

class DietForm(ModelForm):
    class Meta:
        model = DietaryRestriction
        fields = ["vegan", "vegetarian", "gluten_free"]

class IngredientsForm(Form):
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
                self.fields[field_name] = BooleanField(
                    label=ingredient, 
                    initial=wanted, 
                    required=False,
                    widget=forms.CheckboxInput()
                )

class DeadClick(models.Model):
    # All fields are nullable. 
    
    timestamp = models.DateTimeField(null=True) #auto_now_add=True ?
    url = models.URLField(null=True)
    
    # x and y coordinates of the click
    x = models.IntegerField(null=True)
    y = models.IntegerField(null=True)
    
    # DOM element information of the where the click occurred
    tag_name = models.CharField(max_length=255, null=True)
    class_name = models.CharField(max_length=255, null=True)
    element_id = models.CharField(max_length=255, null=True)