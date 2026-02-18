from django import template

register = template.Library()

# Dictionary to hold totals for each category
_accumulator = {}

@register.simple_tag
def reset_totals():
    """Reset the accumulator dictionary."""
    global _accumulator
    _accumulator = {}

@register.simple_tag
def add_to_total(key, value):
    """Add a value to the total for a specific key."""
    global _accumulator
    _accumulator[key] = _accumulator.get(key, 0) + (value or 0)
    return ''  # Return nothing; just accumulate

@register.simple_tag
def get_total(key):
    """Get the total value for a specific key."""
    global _accumulator
    return _accumulator.get(key, 0)

