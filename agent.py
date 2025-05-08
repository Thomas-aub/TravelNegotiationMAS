
import threading
import time
import uuid
from message import Message

class Agent(threading.Thread):
    def __init__(self, agent_id, agent_type, message_board):
        """
        Initialise un agent dans le système de négociation.

        Args:
            agent_id (str): Identifiant unique de l'agent
            agent_type (str): Type de l'agent ("supplier" ou "buyer")
            message_board (SharedMessageBoard): Référence au tableau de messages partagé
        """
        super().__init__()
        self.id = agent_id
        self.type = agent_type
        self.message_board = message_board
        self.active_negotiations = {}  # id_negotiation -> dernier numéro de message
        self.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
        self.running = True
        self.message_board.register_observer(self)

    def notify(self, id_negotiation):
        """
        Méthode appelée quand un nouveau message est ajouté au tableau.

        Args:
            id_negotiation (str): L'identifiant de la négociation mise à jour
        """
        # À implémenter dans les sous-classes
        

    def process_message(self, message):
        """
        Traite un message reçu en fonction de son état.

        Args:
            message (Message): Le message à traiter

        Returns:
            bool: True si la négociation continue, False sinon
        """
        # Si le message est accepté, on affiche le prix accordé et on arrête
        if message.state == "accepted":
            print(f"Agent {self.id}: We agreed on: {message.price}")
            return False

        # Si le message est annulé, on affiche qu'on n'a pas trouvé d'accord et on arrête
        if message.state == "aborted":
            print(f"Agent {self.id}: We could not find an agreement")
            return False

        # Si le nombre de messages restants est 0, on arrête
        if message.message_remaining <= 0:
            print(f"Agent {self.id}: Negotiation timeout")
            return False

        # Sinon, on continue la négociation
        return True

    def send_message(self, id_negotiation, price, state="processing"):
        """
        Envoie un message dans une négociation.

        Args:
            id_negotiation (str): L'identifiant de la négociation
            price (float): Le prix proposé
            state (str): État du message
        """

        # Récupérer le numéro du dernier message et mettre à jour
        last_msg_num = self.active_negotiations.get(id_negotiation, -1)
        new_msg_num = last_msg_num + 1
        self.active_negotiations[id_negotiation] = new_msg_num

        # Récupérer le dernier message pour connaître le nombre de messages restants
        last_message = self.message_board.get_last_message(id_negotiation)
        message_remaining = last_message.message_remaining - 1 if last_message else 9

        # Créer et envoyer le message
        message = Message(
            msg_type=self.type,
            sender_id=self.id,
            id_negotiation=id_negotiation,
            price=price,
            state=state,
            message_number=new_msg_num,
            message_remaining=message_remaining,
            company=self.company if self.type == "supplier" else ""
        )
        self.message_board.add_message(message)
        print(f"Agent {self.id} sent: {message}")

    def stop(self):
        """Arrête le thread de l'agent."""
        self.running = False
