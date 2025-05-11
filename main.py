import time
import csv
import uuid
import random

from coalition import form_buyer_coalitions, form_supplier_coalitions, idp_coalition_formation, token_based_coalition_formation
from shared_board import SharedMessageBoard
from supplier import Supplier
from buyer import Buyer
from buyerCoalition import BuyerCoalition
from output import save_summary_to_csv, save_summary_to_html, save_summary_to_html_bis
from supplierCoalition import SupplierCoalition


def run_single_negotiation():
    message_board = SharedMessageBoard()

    # Création des agents
    supplier = Supplier("supplier_1", message_board, first_price=1000, min_price=500, company="CompanyX", ticket_remaining=3)
    buyer = Buyer("buyer_1", message_board, first_price=300, max_price=600, favourite_companies=["CompanyX"], worst_companies=[], blocked_companies=[])

    supplier.start()
    buyer.start()

    # Affichage des infos
    print("Supplier Information:")
    print(f"Supplier ID: {supplier.id}")
    print(f"Min Price: {supplier.min_price}")
    print(f"Company: {supplier.company}")
    print(f"Tickets Remaining: {supplier.ticket_remaining}")
    print("Buyer Information:")
    print(f"Buyer ID: {buyer.id}")
    print(f"Max Price: {buyer.max_price}")
    print(f"Favorite Companies: {', '.join(buyer.favourite_companies)}")
    print(f"Worst Companies: {', '.join(buyer.worst_companies)}")
    print(f"Blocked Companies: {', '.join(buyer.blocked_companies) if buyer.blocked_companies else 'None'}")
    print("------")
    print("Starting negotiation...")

    # Lancer la négociation
    negotiation_id = supplier.start_negotiation()

    # Attendre la fin de la négociation
    try:
        while True:
            last_msg = message_board.get_last_message(negotiation_id)
            if last_msg and last_msg.state in ["accepted", "aborted"]:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Negotiation interrupted by user")

    # Arrêt des threads
    supplier.stop()
    buyer.stop()

    # Récupération des messages
    print("\nSummary:")
    messages = message_board.get_all_messages(negotiation_id)
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
        supplier = Supplier(f"supplier_{i}", message_board, first_price=min_price * 5, min_price=min_price, strategy_type=strategy, company=f"Company{i}", ticket_remaining=5)
        suppliers.append(supplier)

    # Afficher les informations des fournisseurs
    print("Suppliers Information:")
    for supplier in suppliers:
        print(f"Supplier ID: {supplier.id}")
        print(f"Min Price: {supplier.min_price}")
        print(f"Company: {supplier.company}")
        print(f"Tickets Remaining: {supplier.ticket_remaining}")
        print(f"Strategy: {supplier.strategy_type}")
        print("------")

    # Créer les acheteurs avec différentes stratégies
    buyers = []
    for i in range(num_buyers):
        strategy = "default" if i % 2 == 0 else "default"
        max_price = 600 + (i * 50)  # Différents prix maximums
        buyer = Buyer(f"buyer_{i}", message_board, first_price=max_price*0.5, max_price=max_price, strategy_type=strategy, favourite_companies=[f"Company{i}"], worst_companies=[f"Company{(i+1)%num_suppliers}"], blocked_companies=None)
        buyers.append(buyer)

    # Afficher les informations des acheteurs
    print("Buyers Information:")
    for buyer in buyers:
        print(f"Buyer ID: {buyer.id}")
        print(f"Max Price: {buyer.max_price}")
        print(f"Favorite Companies: {', '.join(buyer.favourite_companies)}")
        print(f"Worst Companies: {', '.join(buyer.worst_companies)}")
        print(f"Blocked Companies: {', '.join(buyer.blocked_companies) if buyer.blocked_companies else 'None'}")
        print(f"Strategy: {buyer.strategy_type}")
        print("------")


    # Démarrer tous les agents
    for agent in suppliers + buyers:
        agent.start()

    # Démarrer les négociations
    negotiations = []
    for supplier in suppliers:
        for _ in range(negotiations_per_supplier):
            id_negotiation = supplier.start_negotiation()
            negotiations.append(id_negotiation)
            time.sleep(0.2)

    # Nouvelle logique pour attendre la fin des négociations
    try:
        start_time = time.time()
        timeout = 10  # 10 secondes de timeout maximum
        active_negotiations = set(negotiations)
        
        while active_negotiations and (time.time() - start_time) < timeout:
            completed = set()
            for id_negotiation in active_negotiations:
                last_message = message_board.get_last_message(id_negotiation)
                if not last_message:
                    continue
                    
                if last_message.state in ["accepted", "aborted"] or last_message.message_remaining <= 0:
                    completed.add(id_negotiation)
                    
            active_negotiations -= completed
            if active_negotiations:
                print(f"Remaining negotiations: {len(active_negotiations)}")
                time.sleep(0.5)
                
        if active_negotiations:
            print(f"Timeout reached, {len(active_negotiations)} negotiations didn't complete")
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
    
    # Save summary to CSV
    save_summary_to_csv(negotiations, message_board, filename="multiple_negotiation_summary.csv")

    # Appel de la fonction pour générer le fichier HTML
    save_summary_to_html_bis(negotiations, message_board, buyers, suppliers, filename="multiple_negotiation_summary.html")




def run_multiple_negotiations_with_coalitions(num_suppliers, num_buyers, negotiations_per_supplier, coalition_algo="coupling", coalition_type="buyers", filename="coalition_analysis.html"):
    message_board = SharedMessageBoard()

    # --- Fournisseurs ---
    suppliers = []
    for i in range(num_suppliers):
        strategy = "conciliatory" if i % 2 == 0 else "default"
        min_price = 300 + (i * 50)
        supplier = Supplier(f"supplier_{i}", message_board, first_price=min_price * 5, min_price=min_price,
                            strategy_type=strategy, company=f"Company{i}", ticket_remaining=5)
        suppliers.append(supplier)

    # --- Acheteurs ---
    buyers = []
    for i in range(num_buyers):
        strategy = "aggressive" if i % 2 == 0 else "default"
        max_price = 600 + (i * 50)
        buyer = Buyer(f"buyer_{i}", message_board, first_price=max_price * 0.5, max_price=max_price,
                      strategy_type=strategy,
                      favourite_companies=[f"Company{i}"],
                      worst_companies=[f"Company{(i + 1) % num_suppliers}"],
                      blocked_companies=[])
        buyers.append(buyer)

    supplier_coalitions = []
    buyer_coalitions = []
    remaining_suppliers = suppliers
    remaining_buyers = buyers

    # --- Formations de coalitions ---
    if coalition_type in ["buyers", "both"]:
        if coalition_algo == "coupling":
            buyer_coalitions, remaining_buyers = form_buyer_coalitions(buyers, max_coalition_size=3)
        elif coalition_algo == "idp":
            buyer_coalitions = idp_coalition_formation(buyers, agent_type="buyer")
            remaining_buyers = [b for b in buyers if not any(b in c.members for c in buyer_coalitions)]
        elif coalition_algo == "token":
            buyer_coalitions = token_based_coalition_formation(buyers, agent_type="buyer")
            remaining_buyers = [b for b in buyers if not any(b in c.members for c in buyer_coalitions)]
        buyer_coalitions = [BuyerCoalition(f"Coalition_B_{i}", message_board, c.members) for i, c in enumerate(buyer_coalitions)]

    if coalition_type in ["suppliers", "both"]:
        if coalition_algo == "coupling":
            supplier_coalitions, remaining_suppliers = form_supplier_coalitions(suppliers, max_coalition_size=2)
        elif coalition_algo == "idp":
            supplier_coalitions = idp_coalition_formation(suppliers, agent_type="supplier")
            remaining_suppliers = [s for s in suppliers if not any(s in c.members for c in supplier_coalitions)]
        elif coalition_algo == "token":
            supplier_coalitions = token_based_coalition_formation(suppliers, agent_type="supplier")
            remaining_suppliers = [s for s in suppliers if not any(s in c.members for c in supplier_coalitions)]
        supplier_coalitions = [SupplierCoalition(f"Coalition_S_{i}", message_board, c.members) for i, c in enumerate(supplier_coalitions)]

    # --- Démarrer les agents ---
    all_agents = remaining_suppliers + supplier_coalitions + remaining_buyers + buyer_coalitions
    for agent in all_agents:
        agent.start()

    # --- Démarrer les négociations ---
    negotiations = []
    for supplier in remaining_suppliers + supplier_coalitions:
        for _ in range(negotiations_per_supplier):
            negotiation_id = supplier.start_negotiation()
            negotiations.append(negotiation_id)
            time.sleep(0.2)

    # --- Attendre la fin ---
    try:
        timeout = 10
        start_time = time.time()
        active = set(negotiations)

        while active and (time.time() - start_time < timeout):
            finished = {n for n in active if (
                (msg := message_board.get_last_message(n)) and
                msg.state in ["accepted", "aborted"]
            )}
            active -= finished
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interruption")

    # --- Arrêter les agents ---
    for agent in all_agents:
        agent.stop()

    # --- Résumé ---
    accepted = 0
    aborted = 0
    final_prices = []

    for id_neg in negotiations:
        messages = message_board.get_all_messages(id_neg)
        if messages:
            last_msg = messages[-1]
            if last_msg.state == "accepted":
                accepted += 1
                final_prices.append(last_msg.price)
            else:
                aborted += 1

    print("\nRésultats des négociations :")
    print(f"  Total : {len(negotiations)}")
    print(f"  Acceptées : {accepted}")
    print(f"  Abandonnées : {aborted}")
    if final_prices:
        print(f"  Prix moyen : {sum(final_prices)/len(final_prices):.2f}")

    save_summary_to_csv(negotiations, message_board,filename="multiple_negotiation_coalition_summary.csv")
    save_summary_to_html(negotiations, message_board, buyers, suppliers, filename)


# --- Lancer les expériences ---
if __name__ == "__main__":

    print("=== Running a single negotiation ===")
    run_single_negotiation()

    print("\n=== Running multiple negotiations ===")
    run_multiple_negotiations(num_suppliers=10, num_buyers=8, negotiations_per_supplier=3)
    
    print("=== Négociations avec coalitions acheteurs (coupling) ===")
    run_multiple_negotiations_with_coalitions(num_suppliers=8, num_buyers=6, negotiations_per_supplier=2,
                                              coalition_algo="coupling", coalition_type="buyers", filename="coalition_analysis_buyer.html")

    print("\n=== Négociations avec coalitions fournisseurs (token) ===")
    run_multiple_negotiations_with_coalitions(num_suppliers=8, num_buyers=6, negotiations_per_supplier=2,
                                              coalition_algo="token", coalition_type="suppliers", filename="coalition_analysis_supplier.html")

    print("\n=== Négociations avec coalitions acheteurs et fournisseurs ===")
    run_multiple_negotiations_with_coalitions(num_suppliers=10, num_buyers=8, negotiations_per_supplier=10,
                                              coalition_algo="idp", coalition_type="both", filename="coalition_analysis_both.html")