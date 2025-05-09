import csv
import os
import io
import base64
import matplotlib.pyplot as plt


def save_summary_to_csv(negotiation_ids, message_board, filename="negotiation_summary.csv"):
    output_dir = "./result"
    os.makedirs(output_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas
    
    full_path = os.path.join(output_dir, filename)
    with open(full_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Negotiation ID", "Final Price", "State", "Buyer ID", "Supplier ID"])

        for neg_id in negotiation_ids:
            messages = message_board.get_all_messages(neg_id)
            if not messages:
                continue
            last_msg = messages[-1]
            buyer_id = next((msg.id for msg in messages if msg.type == "buyer"), "")
            supplier_id = next((msg.id for msg in messages if msg.type == "supplier"), "")
            writer.writerow([neg_id, last_msg.price, last_msg.state, buyer_id, supplier_id])
    print(f"Résumé CSV enregistré dans {full_path}")


def generate_base64_graph(prices, states):
    fig1, ax1 = plt.subplots()
    labels = ["Accepted", "Aborted"]
    sizes = [states.count("accepted"), states.count("aborted")]
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    pie_buf = io.BytesIO()
    plt.savefig(pie_buf, format='png')
    pie_data = base64.b64encode(pie_buf.getvalue()).decode('utf-8')
    plt.close()

    fig2, ax2 = plt.subplots()
    ax2.hist(prices, bins=10, color='skyblue', edgecolor='black')
    ax2.set_title("Distribution des prix finaux (acceptés)")
    ax2.set_xlabel("Prix")
    ax2.set_ylabel("Nombre de négociations")
    hist_buf = io.BytesIO()
    plt.savefig(hist_buf, format='png')
    hist_data = base64.b64encode(hist_buf.getvalue()).decode('utf-8')
    plt.close()

    return pie_data, hist_data

def save_summary_to_html(negotiation_ids, message_board, buyers, suppliers, filename):
    prices = []
    states = []
    rows = ""
    for neg_id in negotiation_ids:
        messages = message_board.get_all_messages(neg_id)
        if not messages:
            continue
        last_msg = messages[-1]
        buyer_id = next((msg.id for msg in messages if msg.type == "buyer"), "")
        supplier_id = next((msg.id for msg in messages if msg.type == "supplier"), "")
        row_class = "accepted" if last_msg.state == "accepted" else "aborted"
        rows += f"<tr class='{row_class}'><td>{neg_id}</td><td>{last_msg.price:.2f}</td><td>{last_msg.state}</td><td>{buyer_id}</td><td>{supplier_id}</td></tr>"
        if last_msg.state == "accepted":
            prices.append(last_msg.price)
        states.append(last_msg.state)

    pie_img, hist_img = generate_base64_graph(prices, states)

    html_content = f"""
    <html>
    <head>
        <title>Analyse des négociations</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .accepted {{ background-color: #d4edda; }}
            .aborted {{ background-color: #f8d7da; }}
        </style>
    </head>
    <body>
        <h1>Résumé des négociations</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Prix Final</th>
                <th>État</th>
                <th>Acheteur</th>
                <th>Fournisseur</th>
            </tr>
            {rows}
        </table>
        <h2>Graphiques</h2>
        <h3>Taux de succès</h3>
        <img src="data:image/png;base64,{pie_img}" width="400"/>
        <h3>Distribution des prix finaux</h3>
        <img src="data:image/png;base64,{hist_img}" width="600"/>
        <h2>Acheteurs</h2>
        <ul>
            {''.join(f'<li>{b.id} - max {b.max_price}</li>' for b in buyers)}
        </ul>
        <h2>Fournisseurs</h2>
        <ul>
            {''.join(f'<li>{s.id} - min {s.min_price}</li>' for s in suppliers)}
        </ul>
    </body>
    </html>
    """

    with open("./result/"+filename, "w") as f:
        f.write(html_content)
    print(f"Résumé HTML avec graphiques sauvegardé dans ./result/{filename}")


def save_summary_to_html_bis(negotiations, message_board, buyers, suppliers, filename="output.html"):
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

    with open("./result/"+filename, "w") as file:
        file.write(html_content)