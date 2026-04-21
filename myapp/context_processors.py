# myapp/context_processors.py
from .models import Cart

def cart_count(request):
    """কার্টের আইটেম সংখ্যা টেমপ্লেটে পাঠান"""
    if request.user.is_authenticated:
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            return {'cart_items_count': cart.total_items}
        except:
            return {'cart_items_count': 0}
    return {'cart_items_count': 0}