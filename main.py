
import time
import csv
import uuid
from shared_board import SharedMessageBoard
from supplier import Supplier
from buyer import Buyer
import random

def run_single_negotiation():
    """
    Exécute une négociation entre un fournisseur et un acheteur.
    """
    # Créer le tableau de messages partagé
    message_board = SharedMessageBoard()

    # Créer un fournisseur et un acheteur
    supplier = Supplier(f"S_toto", message_board, first_price=1500, min_price=500, company="CompanyA", ticket_remaining=5)
    buyer = Buyer(f"B_tintin", message_board, first_price=300, max_price=600, favourite_companies=["CompanyA"], worst_companies=["CompanyB"], blocked_companies=["CompanyC"])

    # Démarrer les threads des agents
    supplier.start()
    buyer.start()

    # Démarrer une négociation
    id_negotiation = supplier.start_negotiation()

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

    # Save summary to CSV
    save_summary_to_csv([id_negotiation], message_board)

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
        timeout = 30  # 30 secondes de timeout maximum
        active_negotiations = set(negotiations)
        
        while active_negotiations and (time.time() - start_time) < timeout:
            completed = set()
            for id_negotiation in active_negotiations:
                last_message = message_board.get_last_message(id_negotiation)
                if not last_message:
                    continue
                    
                if last_message.state in ["accepted", "aborted"] or last_message.message_remaining <= 0:
                    completed.add(id_negotiation)
                    print(f"Negotiation {id_negotiation} completed")
                    
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
    save_summary_to_csv(negotiations, message_board)

    # Appel de la fonction pour générer le fichier HTML
    save_summary_to_html(negotiations, message_board, buyers, suppliers)


def save_summary_to_csv(negotiations, message_board):
    with open("summary.csv", mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Negotiation ID", "Message Number", "Sender ID", "Price", "State", "Company"])

        for id_negotiation in negotiations:
            messages = message_board.get_all_messages(id_negotiation)
            for msg in messages:
                writer.writerow([id_negotiation, msg.message_number, msg.id, msg.price, msg.state, msg.company])


def save_summary_to_html(negotiations, message_board, buyers, suppliers):
    """
    Génère un fichier HTML avec un tableau stylisé des résultats des négociations.
    """
    html_content = """
    <html>
    <head>
        <title>Negotiation Summary</title>
        <style>
            .negotiation-div {
                border: 1px solid #ccc;
                padding: 16px;
                margin-bottom: 20px;
                border-radius: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }
            th {
                background-color: #f2f2f2;
            }
            .accepted {
                background-color: #98FB98; /* Light Green */
            }
            .aborted {
                background-color: #FFB6C1; /* Light Pink */
            }
            .negotiation-type {
                font-size: 1.2em;
                margin-bottom: 10px;
                padding: 8px;
                border-radius: 4px;
                background-color: #e6f3ff;
            }
            .one-to-one {
                border-left: 5px solid #4CAF50;
            }
            .one-to-coalition {
                border-left: 5px solid #FF9800;
            }
        </style>
    </head>
    <body>
        <h1>Negotiation Summary</h1>
    """


    # --- Section de résumé ---
    accepted = 0
    aborted = 0
    final_prices = []

    for id_negotiation in negotiations:
        messages = message_board.get_all_messages(id_negotiation)
        if not messages:
            continue
        last_message = messages[-1]
        if last_message.state == "accepted":
            accepted += 1
            final_prices.append(last_message.price)
        else:
            aborted += 1

    total = len(negotiations)
    avg_price = sum(final_prices) / len(final_prices) if final_prices else 0
    min_price = min(final_prices) if final_prices else 0
    max_price = max(final_prices) if final_prices else 0

    html_content += f"""
        <div style='padding:20px; border-radius:8px; margin-bottom:30px;'>
            <h2>Statistiques Générales</h2>
            <ul>
                <li><strong>Total des négociations :</strong> {total}</li>
                <li><strong>Acceptées :</strong> {accepted} ({(accepted/total)*100:.1f}%)</li>
                <li><strong>Annulées :</strong> {aborted} ({(aborted/total)*100:.1f}%)</li>
                <li><strong>Prix moyen final :</strong> {avg_price:.2f}</li>
                <li><strong>Prix minimum :</strong> {min_price:.2f}</li>
                <li><strong>Prix maximum :</strong> {max_price:.2f}</li>
            </ul>
        </div>
    """


    for id_negotiation in negotiations:
        # Trouver le supplier et le(s) buyer(s) participants
        participants = message_board.get_negotiation_participants(id_negotiation)
        supplier = next((s for s in suppliers if s.id in participants), None)
        buyers_in_negotiation = [b for b in buyers if b.id in participants]
        
        # Déterminer le type de négociation
        negotiation_type = "one-to-one" if len(buyers_in_negotiation) == 1 else "one-to-coalition"
        type_label = "1-to-1" if negotiation_type == "one-to-one" else "1-to-Coalition"
        
        messages = message_board.get_all_messages(id_negotiation)
        last_message = messages[-1] if messages else None
        negotiation_status = "accepted" if last_message and last_message.state == "accepted" else "aborted"

        html_content += f"""
        <div class="negotiation-div">
            <div class="negotiation-type {negotiation_type}">
                <strong>Negotiation Type:</strong> {type_label} |
                <strong>ID:</strong> {id_negotiation} |
                <strong>Status:</strong> {negotiation_status} |
                <strong>Final Price:</strong> {last_message.price if last_message else 'N/A'}
            </div>
            
            <h3>Supplier Information:</h3>
            <p><strong>Supplier ID:</strong> {supplier.id if supplier else 'N/A'}</p>
            <p><strong>Min Price:</strong> {supplier.min_price if supplier else 'N/A'}</p>
            <p><strong>Company:</strong> {supplier.company if supplier else 'N/A'}</p>
            <p><strong>Tickets Remaining:</strong> {supplier.ticket_remaining if supplier else 'N/A'}</p>
            <p><strong>Strategy:</strong> {supplier.strategy_type if supplier else 'N/A'}</p>

            <h3>Buyer(s) Information:</h3>
        """

        for buyer in buyers_in_negotiation:
            html_content += f"""
            <div style="margin-bottom: 15px;">
                <p><strong>Buyer ID:</strong> {buyer.id}</p>
                <p><strong>Max Price:</strong> {buyer.max_price}</p>
                <p><strong>Favorite Companies:</strong> {', '.join(buyer.favourite_companies)}</p>
                <p><strong>Worst Companies:</strong> {', '.join(buyer.worst_companies)}</p>
                <p><strong>Blocked Companies:</strong> {', '.join(buyer.blocked_companies) if buyer.blocked_companies else 'None'}</p>
                <p><strong>Strategy:</strong> {buyer.strategy_type}</p>
            </div>
            """

        html_content += """
            <h3>Negotiation Messages:</h3>
            <table class="{negotiation_status}">
                <tr>
                    <th>Message Number</th>
                    <th>Sender ID</th>
                    <th>Price</th>
                    <th>State</th>
                    <th>Company</th>
                    <th>Message Type</th>
                </tr>
        """

        for msg in messages:
            message_type = "Counter-offer"
            if msg.message_number == 0:
                message_type = "Initial offer"
            elif msg.state in ["accepted", "aborted"]:
                message_type = "Final agreement" if msg.state == "accepted" else "Aborted"

            row_style = f"background-color: {'#98FB98' if negotiation_status == 'accepted' else '#FFB6C1'};"
            if msg.type == "buyer":
                row_style += " color: gray;"

            html_content += f"""
                <tr style="{row_style}">
                    <td>{msg.message_number}</td>
                    <td>{msg.id}</td>
                    <td>{msg.price}</td>
                    <td>{msg.state}</td>
                    <td>{msg.company}</td>
                    <td>{message_type}</td>
                </tr>
            """

        html_content += """
            </table>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    with open("negotiation_summary.html", "w") as file:
        file.write(html_content)
# Appel de la fonction pour générer le fichier HTML
# Assurez-vous de passer les listes de buyers et suppliers lors de l'appel de la fonction
# save_summary_to_html(negotiations, message_board, buyers, suppliers)



if __name__ == "__main__":
    print("=== Running a single negotiation ===")
    # run_single_negotiation()

    print("\n=== Running multiple negotiations ===")
    run_multiple_negotiations(num_suppliers=20, num_buyers=8, negotiations_per_supplier=3)
