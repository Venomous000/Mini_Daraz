from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    return float(value) * int(arg)

@register.filter
def calc_cart_total(items):
    return sum(item.unit_price * item.quantity for item in items)