from django import template

register = template.Library()


@register.filter
def sum_prices(queryset):
    total_prices = []
    for item in queryset:
        total_prices.append(item.price * item.quantity)
    return sum(total_prices)
