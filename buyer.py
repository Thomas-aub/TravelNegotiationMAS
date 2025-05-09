from agent import Agent
import time
import strategies

class Buyer(Agent):
    def __init__(self, agent_id, message_board, max_price, first_price, strategy_type="default", favourite_companies=None, worst_companies=None, blocked_companies=None):
        """
        Initialise un agent acheteur.

        Args:
            agent_id (str): Identifiant unique de l'agent
            message_board (SharedMessageBoard): Référence au tableau de messages partagé
            max_price (float): Prix maximum que l'acheteur est prêt à payer
            first_price (float): Prix de départ auquel le fournisseur est prêt à vendre
            strategy_type (str): Type de stratégie à utiliser
            favourite_companies (list): Liste des compagnies préférées
            worst_companies (list): Liste des compagnies les moins préférées
            blocked_companies (list): Liste des compagnies bloquées
        """
        super().__init__(agent_id, "buyer", message_board)
        self.max_price = max_price
        self.strategy_type = strategy_type
        self.current_price = first_price
        self.negotiations_to_process = set()
        self.favourite_companies = favourite_companies or []
        self.worst_companies = worst_companies or []
        self.blocked_companies = blocked_companies or []


    def run(self):
        """Point d'entrée du thread de l'acheteur."""
        while self.running:
            # Traiter toutes les négociations en attente
            negotiations = self.negotiations_to_process.copy()
            for id_negotiation in negotiations:
                self.handle_negotiation(id_negotiation)
                self.negotiations_to_process.remove(id_negotiation)

            time.sleep(0.1)  # Petite pause pour éviter une consommation CPU excessive

    def notify(self, id_negotiation):
        """
        Traite les notifications de nouveaux messages.

        Args:
            id_negotiation (str): L'identifiant de la négociation mise à jour
        """
        # Vérifier si l'agent est déjà participant à cette négociation
        # OU si aucun participant n'est encore enregistré (pour permettre aux acheteurs de rejoindre une nouvelle négociation)
        if (self.message_board.is_participant(id_negotiation, self.id) or
            len(self.message_board.get_negotiation_participants(id_negotiation)) == 1):  # Seulement le fournisseur est enregistré
            self.negotiations_to_process.add(id_negotiation)

    def handle_negotiation(self, id_negotiation):
        """
        Gère une négociation spécifique.

        Args:
            id_negotiation (str): L'identifiant de la négociation à traiter
        """
        last_message = self.message_board.get_last_message(id_negotiation)

        if (len(self.message_board.get_negotiation_participants(id_negotiation)) == 1) :
            self.message_board.register_participant(id_negotiation, self.id)
            
        # Ne traiter que si nous sommes participants ou si c'est une nouvelle négociation
        if not (self.message_board.is_participant(id_negotiation, self.id) or
            len(self.message_board.get_negotiation_participants(id_negotiation)) == 1):
            
            # Vérifier qu'il n'y a pas déjà d'autre buyer
            participants = self.message_board.get_negotiation_participants(id_negotiation)
            if any(p.startswith('B_') or p.startswith('buyer_') for p in participants if p != self.id):
                return
            self.message_board.register_participant(id_negotiation, self.id)
            self.active_negotiations[id_negotiation] = -1

        # Ignorer les messages qui ne sont pas du supplier
        if last_message.type != "supplier":
            return

        if not self.process_message(last_message):
            return

        # Appliquer la stratégie
        if self.strategy_type == "default":
            response_price, state = strategies.buyer_default_strategy(
                self.current_price, self.max_price, last_message.price,
                self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
            )
        elif self.strategy_type == "aggressive":
            response_price, state = strategies.buyer_aggressive_strategy(
                self.current_price, self.max_price, last_message.price,
                self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
            )
        else:
            response_price, state = strategies.buyer_default_strategy(
                self.current_price, self.max_price, last_message.price,
                self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
            )

        self.send_message(id_negotiation, response_price, state)

        if state == "processing":
            self.current_price = response_price

            """
            Gère une négociation spécifique.
            """
            last_message = self.message_board.get_last_message(id_negotiation)
            
            # Ne traiter que si nous sommes participants ou si c'est une nouvelle négociation
            if not (self.message_board.is_participant(id_negotiation, self.id) or 
                len(self.message_board.get_negotiation_participants(id_negotiation)) == 1):
                # Vérifier qu'il n'y a pas déjà d'autre buyer
                participants = self.message_board.get_negotiation_participants(id_negotiation)
                if any(p.startswith('B_') or p.startswith('buyer_') for p in participants if p != self.id):
                    return
                self.message_board.register_participant(id_negotiation, self.id)
                self.active_negotiations[id_negotiation] = -1
            
            # Ignorer les messages qui ne sont pas du supplier
            if last_message.type != "supplier":
                return
            
            if not self.process_message(last_message):
                return

            # Appliquer la stratégie
            if self.strategy_type == "default":
                response_price, state = strategies.buyer_default_strategy(
                    self.current_price, self.max_price, last_message.price,
                    self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
                )
            elif self.strategy_type == "aggressive":
                response_price, state = strategies.buyer_aggressive_strategy(
                    self.current_price, self.max_price, last_message.price,
                    self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
                )
            else:
                response_price, state = strategies.buyer_default_strategy(
                    self.current_price, self.max_price, last_message.price,
                    self.favourite_companies, self.worst_companies, self.blocked_companies, last_message.company
                )

            self.send_message(id_negotiation, response_price, state)

            if state == "processing":
                self.current_price = response_price