import time
import uuid
from shared_board import SharedMessageBoard
from supplier import Supplier
from buyer import Buyer

def run_single_negotiation():
    """
    Exécute une négociation entre un fournisseur et un acheteur.
    """
    # Créer le tableau de messages partagé
    message_board = SharedMessageBoard()
    
    # Créer un fournisseur et un acheteur
    supplier = Supplier(f"S_toto", message_board, first_price=1500, min_price=500)
    buyer = Buyer(f"B_tintin", message_board, first_price=300, max_price=600)
    
    # Démarrer les threads des agents
    supplier.start()
    buyer.start()
    
    # Démarrer une négociation
    id_negotiation = supplier.start_negotiation("nego1")
    
    # Attendre que la négociation se termine
    try:
        while True:
            # Vérifier si la négociation est terminée
            last_message = message_board.get_last_message(id_negotiation)
            if last_message and last_message.state in ["accepted", "aborted"] or \
               (last_message and last_message.message_remaining <= 0):
                break
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Negotiation interrupted by user")
    
    # Arrêter les agents proprement
    supplier.stop()
    buyer.stop()
    
    # Afficher les résultats
    print("\nNegotiation complete. Summary:")
    messages = message_board.get_all_messages(id_negotiation)
    for msg in messages:
        print(f"  {msg}")

def run_multiple_negotiations(num_suppliers, num_buyers, negotiations_per_supplier):
    """
    Exécute plusieurs négociations entre plusieurs fournisseurs et acheteurs.
    
    Args:
        num_suppliers (int): Nombre de fournisseurs
        num_buyers (int): Nombre d'acheteurs
        negotiations_per_supplier (int): Nombre de négociations par fournisseur
    """
    # Créer le tableau de messages partagé
    message_board = SharedMessageBoard()
    
    # Créer les fournisseurs avec différentes stratégies
    suppliers = []
    for i in range(num_suppliers):
        strategy = "conciliatory" if i % 2 == 0 else "default"
        min_price = 300 + (i * 50)  # Différents prix minimums
        supplier = Supplier(f"supplier_{i}", message_board, first_price=min_price * 5, min_price=min_price, strategy_type=strategy)
        suppliers.append(supplier)
    
    # Créer les acheteurs avec différentes stratégies
    buyers = []
    for i in range(num_buyers):
        strategy = "aggressive" if i % 2 == 0 else "default"
        max_price = 600 + (i * 50)  # Différents prix maximums
        buyer = Buyer(f"buyer_{i}", message_board, first_price=max_price*0.5, max_price=max_price, strategy_type=strategy)
        buyers.append(buyer)
    
    # Démarrer tous les agents
    for agent in suppliers + buyers:
        agent.start()
    
    # Démarrer les négociations
    negotiations = []
    for supplier in suppliers:
        for _ in range(negotiations_per_supplier):
            id_negotiation = supplier.start_negotiation()
            negotiations.append(id_negotiation)
            time.sleep(0.2)  # Petit délai entre les négociations
    
    # Attendre que toutes les négociations se terminent
    try:
        active_negotiations = set(negotiations)
        while active_negotiations:
            for id_negotiation in list(active_negotiations):
                last_message = message_board.get_last_message(id_negotiation)
                if last_message and last_message.state in ["accepted", "aborted"] or \
                   (last_message and last_message.message_remaining <= 0):
                    active_negotiations.remove(id_negotiation)
            
            time.sleep(0.5)
            print(f"Remaining negotiations: {len(active_negotiations)}")
    except KeyboardInterrupt:
        print("Negotiations interrupted by user")
    
    # Arrêter tous les agents
    for agent in suppliers + buyers:
        agent.stop()
    
    # Calculer des statistiques
    accepted_count = 0
    aborted_count = 0
    final_prices = []
    
    for id_negotiation in negotiations:
        messages = message_board.get_all_messages(id_negotiation)
        if not messages:
            continue
            
        last_message = messages[-1]
        if last_message.state == "accepted":
            accepted_count += 1
            final_prices.append(last_message.price)
        else:
            aborted_count += 1
    
    # Afficher les résultats
    print("\nNegotiations complete. Summary:")
    print(f"  Total negotiations: {len(negotiations)}")
    print(f"  Accepted: {accepted_count} ({accepted_count/len(negotiations)*100:.1f}%)")
    print(f"  Aborted: {aborted_count} ({aborted_count/len(negotiations)*100:.1f}%)")
    
    if final_prices:
        avg_price = sum(final_prices) / len(final_prices)
        print(f"  Average final price: {avg_price:.2f}")
        print(f"  Min price: {min(final_prices):.2f}")
        print(f"  Max price: {max(final_prices):.2f}")

if __name__ == "__main__":
    print("=== Running a single negotiation ===")
    run_single_negotiation()
    
    print("\n=== Running multiple negotiations ===")
    run_multiple_negotiations(num_suppliers=20, num_buyers=3, negotiations_per_supplier=5)