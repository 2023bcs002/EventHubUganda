from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='ugx')
def format_ugx(amount):
    """Format amount in UGX with thousands separator."""
    if not amount:
        return '0'
    try:
        amount = Decimal(str(amount))
        # Format with commas for thousands
        return "{:,.0f}".format(amount)
    except:
        return '0'

@register.simple_tag
def currency_symbol():
    """Return the UGX currency symbol."""
    return 'UGX' 