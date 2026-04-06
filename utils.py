from config import PRODUCTS, CURRENCY_SYMBOL

def format_cart_summary(cart: dict, total: int) -> str:
    lines = ["ORDER SUMMARY:"]
    for pid, qty in cart.items():
        product = PRODUCTS.get(pid)
        if not product:
            continue
        price = product["price"]
        lines.append(f"{qty}x {pid} ({price * qty} {CURRENCY_SYMBOL})")
    lines.append(f"\nTOTAL: {total} {CURRENCY_SYMBOL}")
    return "\n".join(lines)

def format_usdt_amount(rub_amount: int) -> float:
    # пример курса 1 USDT = 90 RUB
    return round(rub_amount / 90, 2)
