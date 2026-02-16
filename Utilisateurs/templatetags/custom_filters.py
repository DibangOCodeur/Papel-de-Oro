from django import template

register = template.Library()

@register.filter
def format_number(value):
    """Formatte un nombre avec des espaces comme séparateur de milliers."""
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return "0"