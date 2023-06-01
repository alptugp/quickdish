from django import template

register = template.Library()

@register.filter
def dict_lookup(dictionary, key):
    return dictionary[key]