from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    try:
        return field.as_widget(attrs={'class': css_class})
    except AttributeError:
        return field  # lo devuelve como está, evita el error