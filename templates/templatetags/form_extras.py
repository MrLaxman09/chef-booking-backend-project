{% comment %} from django import template

register = template.Library()

@register.filter
def placeholder(value, token):
    return value.as_widget(attrs={'placeholder': token}) {% endcomment %}
