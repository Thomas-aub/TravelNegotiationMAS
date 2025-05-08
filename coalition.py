class Coalition:
    def __init__(self, members, coalition_id):
        """
        Initialise une coalition d'agents acheteurs.

        Args:
            members (list): Liste des agents membres de la coalition
            coalition_id (str): Identifiant unique de la coalition
        """
        self.members = members
        self.id = coalition_id
        self.type = "buyer"
        self.max_price = self.calculate_max_price()
        self.current_price = self.max_price * 0.5  # Prix initial
        self.favourite_companies = self.aggregate_preferences("favourite_companies")
        self.worst_companies = self.aggregate_preferences("worst_companies")
        self.blocked_companies = self.aggregate_preferences("blocked_companies")

    def aggregate_preferences(self, pref_type):
        """
        Agrège les préférences des membres de la coalition.
        
        Args:
            pref_type (str): Type de préférence ('favourite', 'worst', 'blocked')
            
        Returns:
            set: Ensemble des compagnies dans cette catégorie
        """
        pref_set = set()
        for member in self.members:
            pref_set.update(getattr(member, pref_type, []))
        return list(pref_set)

    def calculate_max_price(self):
        """
        Calcule le prix maximum que la coalition est prête à payer.
        
        Returns:
            float: Prix maximum
        """
        # On prend la moyenne des prix max des membres avec une légère réduction
        total = sum(member.max_price for member in self.members)
        return total * 0.9 / len(self.members)  # 10% de réduction grâce à la coalition

    def notify(self, id_negotiation):
        """
        Notifie la coalition d'un nouveau message.
        """
        # Déléguer la notification à tous les membres
        for member in self.members:
            member.notify(id_negotiation)

    def send_message(self, id_negotiation, price, state="processing"):
        """
        Envoie un message au nom de la coalition.
        """
        # Utiliser le premier membre comme représentant pour l'envoi
        self.members[0].send_message(id_negotiation, price, state)

def form_buyer_coalitions(buyers, max_size=3):
    """
    Forme des coalitions d'acheteurs.
    
    Args:
        buyers (list): Liste des acheteurs disponibles
        max_size (int): Taille maximale d'une coalition
        
    Returns:
        list: Liste des coalitions formées et acheteurs restants
    """
    coalitions = []
    remaining_buyers = buyers.copy()
    
    # Trier les acheteurs par prix maximum décroissant
    remaining_buyers.sort(key=lambda b: b.max_price, reverse=True)
    
    while len(remaining_buyers) >= 2:  # Au moins 2 acheteurs pour former une coalition
        # Prendre les max_size premiers acheteurs
        coalition_members = remaining_buyers[:max_size]
        coalition_id = f"Coalition_{len(coalitions)+1}"
        new_coalition = Coalition(coalition_members, coalition_id)
        coalitions.append(new_coalition)
        remaining_buyers = remaining_buyers[max_size:]
    
    return coalitions, remaining_buyers