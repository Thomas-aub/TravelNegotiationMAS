def buyer_default_strategy(current_price, max_price, supplier_price, favourite_companies, worst_companies, blocked_companies, company):
    if company in blocked_companies:
        return 0, "aborted"

    if company in favourite_companies:
        supplier_price *= 0.95
    elif company in worst_companies:
        supplier_price *= 1.05

    if supplier_price > current_price:
        if supplier_price > max_price:
            new_price = (supplier_price + current_price) * 0.5  # essayer de se rapprocher
            if new_price > max_price:
                return max_price, "processing"
            return new_price, "processing"
        else:
            return supplier_price, "accepted"
    elif supplier_price == current_price:
        return supplier_price, "accepted"
    else:
        return supplier_price, "accepted"


def supplier_default_strategy(current_price, min_price, buyer_price):
    if buyer_price < current_price:
        if buyer_price < min_price:
            if buyer_price < min_price * 0.7:
                return min_price, "processing"  # éviter d'abandonner trop vite
            return min_price, "processing"
        else:
            new_price = buyer_price + (current_price - buyer_price) * 0.5  # céder à mi-chemin
            return max(new_price, min_price), "processing"
    elif buyer_price == current_price:
        return buyer_price, "accepted"
    else:
        return buyer_price, "accepted"


def buyer_aggressive_strategy(current_price, max_price, supplier_price, favourite_companies, worst_companies, blocked_companies, company):
    if company in blocked_companies:
        return 0, "aborted"

    if company in favourite_companies:
        supplier_price *= 0.95
    elif company in worst_companies:
        supplier_price *= 1.05

    if supplier_price > current_price:
        new_price = current_price + (supplier_price - current_price) * 0.5  # augmenter plus vite
        if new_price > max_price:
            return max_price, "processing"
        return new_price, "processing"
    else:
        return supplier_price, "accepted"


def supplier_conciliatory_strategy(current_price, min_price, buyer_price):
    if buyer_price < min_price:
        adjusted_min = min_price * 0.95
        if buyer_price < adjusted_min:
            new_price = buyer_price + (adjusted_min - buyer_price) * 0.5  # céder progressivement
            return max(new_price, min_price), "processing"
        else:
            return buyer_price, "accepted"
    else:
        return buyer_price, "accepted"