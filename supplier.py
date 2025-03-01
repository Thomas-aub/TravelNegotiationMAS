from agent import Agent
import time
import strategies

class Supplier(Agent):
    def __init__(self, agent_id, message_board, min_price, first_price, strategy_type="default"):
        """
        Initialise un agent fournisseur.
        
        Args:
            agent_id (str): Identifiant unique de l'agent
            message_board (SharedMessageBoard): Référence au tableau de messages partagé
            min_price (float): Prix minimum auquel le fournisseur est prêt à vendre
            first_price (float): Prix de départ auquel le fournisseur est prêt à vendre
            strategy_type (str): Type de stratégie à utiliser
        """
        super().__init__(agent_id, "supplier", message_board)
        self.min_price = min_price
        self.strategy_type = strategy_type
        self.current_price = first_price
        self.negotiations_to_process = set()
    
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
            # Traiter toutes les négociations en attente
            negotiations = self.negotiations_to_process.copy()
            for id_negotiation in negotiations:
                self.handle_negotiation(id_negotiation)
                self.negotiations_to_process.remove(id_negotiation)
            
            time.sleep(0.1)  # Petite pause pour éviter une consommation CPU excessive
    
    def handle_negotiation(self, id_negotiation):
        """
        Gère une négociation spécifique.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation à traiter
        """
        last_message = self.message_board.get_last_message(id_negotiation)
        
        # Ignorer les messages qui ne sont pas de l'acheteur, sauf si c'est le premier message
        if last_message.type != "buyer" and last_message.message_number > 0:
            return
        
        # Vérifier si la négociation doit continuer
        if not self.process_message(last_message):
            return
        
        # Pour le premier message ou après un message de l'acheteur
        if last_message.message_number == 0 and last_message.type == "supplier":
            # C'est notre premier message, on ne fait rien
            return
        
        # Appliquer la stratégie de négociation
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
        
        # Envoyer la réponse
        self.send_message(id_negotiation, response_price, state)
        
        # Mettre à jour le prix actuel si toujours en négociation
        if state == "processing":
            self.current_price = response_price
    
    def start_negotiation(self, id_negotiation=None):
        """
        Démarre une nouvelle négociation.
        
        Args:
            id_negotiation (str, optional): L'identifiant de la négociation à créer
            
        Returns:
            str: L'identifiant de la négociation créée
        """
        if id_negotiation is None:
            id_negotiation = f"nego_{self.id}_{int(time.time())}"
        
        # Initialiser le compteur de messages pour cette négociation
        self.active_negotiations[id_negotiation] = -1
        
        # Envoyer le premier message avec le prix initial
        self.send_message(id_negotiation, self.current_price)
        
        return id_negotiation