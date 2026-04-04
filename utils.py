from config import PRODUCTS, CURRENCY_SYMBOL

def format_cart(cart: dict) -> str:
    if not cart:
        return "Корзина пуста"
    lines = []
    total = 0
    for pid, qty in cart.items():
        product = PRODUCTS.get(pid)
        if not product:
            continue
        price = product["price"]
        subtotal = price * qty
        total += subtotal
        lines.append(f"{product['name']} x{qty} = {subtotal} {CURRENCY_SYMBOL}")
    lines.append(f"\n*ИТОГО: {total} {CURRENCY_SYMBOL}*")
    return "\n".join(lines)
