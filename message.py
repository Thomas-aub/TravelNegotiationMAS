
class Message:
    def __init__(self, msg_type, sender_id, id_negotiation, price, state="processing", message_number=0, message_remaining=10, company=""):
        """
        Initialise un message dans le système de négociation.

        Args:
            msg_type (str): Type de l'agent émetteur ("supplier" ou "buyer")
            sender_id (str): Identifiant unique de l'agent émetteur
            id_negotiation (str): Identifiant unique de la négociation
            price (float): Prix proposé dans le message
            state (str): État du message ("processing", "accepted" ou "aborted")
            message_number (int): Numéro séquentiel du message dans la négociation
            message_remaining (int): Nombre de messages restants avant annulation
            company (str): Nom de la compagnie du fournisseur
        """
        self.type = msg_type
        self.id = sender_id
        self.message_number = message_number
        self.id_negotiation = id_negotiation
        self.price = price
        self.message_remaining = message_remaining
        self.state = state
        self.company = company
        

    def __str__(self):
        """Représentation textuelle du message pour le débogage."""
        if str(self.state) == "accepted":
                return f"------ END OF NEGOCIATION : {self.id_negotiation} - Sold for ${self.price} by {self.company} ------"
        if str(self.state) == "aborted":
            return f"------ END OF NEGOCIATION : {self.id_negotiation} - No agreement reached ------"

        if self.type == "buyer" :
            return f"{self.type}.{self.id} offers to pay ${self.price} ({self.message_remaining} messages left, state:{self.state})"

        return f"{self.type}.{self.id} offers to sell for ${self.price} ({self.message_remaining} messages left, state:{self.state}) from {self.company}"
