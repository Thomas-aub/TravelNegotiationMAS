def buyer_default_strategy(current_price, max_price, supplier_price):
    """
    Stratégie par défaut pour l'acheteur.
    
    Args:
        current_price (float): Prix actuel de l'acheteur
        max_price (float): Prix maximum de l'acheteur
        supplier_price (float): Prix proposé par le fournisseur
        
    Returns:
        tuple: (nouveau prix, état)
    """
    # Si le prix du fournisseur est supérieur au prix actuel de l'acheteur
    if supplier_price > current_price:
        # Si le prix du fournisseur est supérieur au prix maximum
        if supplier_price > max_price:
            # Proposer une réduction de 50%
            new_price = supplier_price * 0.5
            return new_price, "processing"
        else:
            # Le prix est inférieur au max, on accepte
            return supplier_price, "accepted"
    
    # Si le prix est égal au prix actuel, on accepte
    elif supplier_price == current_price:
        return supplier_price, "accepted"
    
    # Si le prix du fournisseur est inférieur au prix actuel
    else:
        # On accepte car c'est un bon prix
        return supplier_price, "accepted"

def buyer_aggressive_strategy(current_price, max_price, supplier_price):
    """
    Stratégie agressive pour l'acheteur.
    
    Args:
        current_price (float): Prix actuel de l'acheteur
        max_price (float): Prix maximum de l'acheteur
        supplier_price (float): Prix proposé par le fournisseur
        
    Returns:
        tuple: (nouveau prix, état)
    """
    # Si le prix du fournisseur est supérieur au prix actuel
    if supplier_price > current_price:
        # On propose toujours une réduction forte, quelle que soit la différence
        new_price = max(current_price, supplier_price * 0.7)
        
        # Si le nouveau prix est toujours supérieur au max, on annule
        if new_price > max_price:
            return 0, "aborted"
        
        return new_price, "processing"
    
    # Si le prix est égal ou inférieur, on accepte
    else:
        return supplier_price, "accepted"

def supplier_default_strategy(current_price, min_price, buyer_price):
    """
    Stratégie par défaut pour le fournisseur.
    
    Args:
        current_price (float): Prix actuel du fournisseur
        min_price (float): Prix minimum du fournisseur
        buyer_price (float): Prix proposé par l'acheteur
        
    Returns:
        tuple: (nouveau prix, état)
    """
    # Si le prix de l'acheteur est inférieur au prix actuel du fournisseur
    if buyer_price < current_price:
        # Si le prix de l'acheteur est inférieur au prix minimum
        if buyer_price < min_price:
            # Si l'écart est grand, on annule
            if buyer_price < min_price * 0.7:
                return 0, "aborted"
            
            # Sinon, on propose notre prix minimum
            return min_price, "processing"
        else:
            # Le prix est supérieur au min, on fait un compromis
            new_price = (current_price + buyer_price) / 2
            return new_price, "processing"
    
    # Si le prix est égal au prix actuel, on accepte
    elif buyer_price == current_price:
        return buyer_price, "accepted"
    
    # Si le prix de l'acheteur est supérieur au prix actuel (rare mais possible)
    else:
        # On accepte car c'est un bon prix
        return buyer_price, "accepted"

def supplier_conciliatory_strategy(current_price, min_price, buyer_price):
    """
    Stratégie conciliante pour le fournisseur.
    
    Args:
        current_price (float): Prix actuel du fournisseur
        min_price (float): Prix minimum du fournisseur
        buyer_price (float): Prix proposé par l'acheteur
        
    Returns:
        tuple: (nouveau prix, état)
    """
    # Si le prix de l'acheteur est inférieur au prix minimum
    if buyer_price < min_price:
        # On est prêt à diminuer notre minimum de 5%
        adjusted_min = min_price * 0.95
        
        if buyer_price < adjusted_min:
            # On propose un prix légèrement au-dessus du prix ajusté
            return adjusted_min, "processing"
        else:
            # On accepte même si c'est un peu en dessous du min initial
            return buyer_price, "accepted"
    
    # Si le prix est au-dessus du minimum, on accepte
    else:
        return buyer_price, "accepted"