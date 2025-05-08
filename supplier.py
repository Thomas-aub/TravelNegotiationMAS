from agent import Agent
import time
import strategies

class Supplier(Agent):
    def __init__(self, agent_id, message_board, min_price, first_price, strategy_type="default", company="", ticket_remaining=10):
        """
        Initialise un agent fournisseur.

        Args:
            agent_id (str): Identifiant unique de l'agent
            message_board (SharedMessageBoard): Référence au tableau de messages partagé
            min_price (float): Prix minimum auquel le fournisseur est prêt à vendre
            first_price (float): Prix de départ auquel le fournisseur est prêt à vendre
            strategy_type (str): Type de stratégie à utiliser
            company (str): Nom de la compagnie du fournisseur
            ticket_remaining (int): Nombre de tickets restants
        """
        super().__init__(agent_id, "supplier", message_board)
        self.min_price = min_price
        self.strategy_type = strategy_type
        self.current_price = first_price
        self.negotiations_to_process = set()
        self.company = company
        self.ticket_remaining = ticket_remaining

    def notify(self, id_negotiation):
        """
        Traite les notifications de nouveaux messages.

        Args:
            id_negotiation (str): L'identifiant de la négociation mise à jour
        """
        self.negotiations_to_process.add(id_negotiation)

    def run(self):
        """Point d'entrée du thread du fournisseur."""
        while self.running:
            negotiations = self.negotiations_to_process.copy()
            for id_negotiation in negotiations:
                self.handle_negotiation(id_negotiation)
                self.negotiations_to_process.remove(id_negotiation)
            time.sleep(0.1)

    def handle_negotiation(self, id_negotiation):
        """
        Gère une négociation spécifique.
        """
        last_message = self.message_board.get_last_message(id_negotiation)
        
        # Ne traiter que les négociations où ce supplier est participant
        if not self.message_board.is_participant(id_negotiation, self.id):
            return
        
        # Ignorer les messages qui ne sont pas des acheteurs ou notre propre message initial
        if last_message.type not in ["buyer", "supplier"]:
            return
        
        # Si c'est notre propre message initial, ne rien faire
        if last_message.type == "supplier" and last_message.id == self.id:
            return
        
        if not self.process_message(last_message):
            return

        # Appliquer la stratégie
        if self.strategy_type == "default":
            response_price, state = strategies.supplier_default_strategy(
                self.current_price, self.min_price, last_message.price
            )
        elif self.strategy_type == "conciliatory":
            response_price, state = strategies.supplier_conciliatory_strategy(
                self.current_price, self.min_price, last_message.price
            )
        else:
            response_price, state = strategies.supplier_default_strategy(
                self.current_price, self.min_price, last_message.price
            )

        self.send_message(id_negotiation, response_price, state)

        if state == "processing":
            self.current_price = response_price
        elif state == "accepted":
            self.ticket_remaining -= 1
            if self.ticket_remaining <= 0:
                print(f"Supplier {self.id} has no more tickets to sell.")

                
    def start_negotiation(self):
        """
        Démarre une nouvelle négociation.
        
        Returns:
            str: L'identifiant de la négociation créée
        """
        id_negotiation = self.message_board.get_next_negotiation_id()
        self.active_negotiations[id_negotiation] = -1

        # Enregistrer le fournisseur comme participant
        self.message_board.register_participant(id_negotiation, self.id)
        self.send_message(id_negotiation, self.current_price)
        return id_negotiation