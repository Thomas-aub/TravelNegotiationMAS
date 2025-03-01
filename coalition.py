class Coalition:
    def __init__(self, members, coalition_type):
        """
        Initialise une coalition d'agents.
        
        Args:
            members (list): Liste des agents membres de la coalition
            coalition_type (str): Type de la coalition ("supplier" ou "buyer")
        """
        self.members = members
        self.type = coalition_type
        self.value = self.calculate_value()
    
    def calculate_value(self):
        """
        Calcule la valeur de la coalition en fonction des profils des membres.
        
        Returns:
            float: Valeur de la coalition
        """
        # Valeur de base proportionnelle au nombre de membres
        base_value = len(self.members) * 10
        
        # Ajouter des bonus en fonction du type
        if self.type == "buyer":
            # Plus la coalition d'acheteurs est grande, plus la réduction est importante
            return base_value * (1 + 0.05 * len(self.members))
        else:
            # Les fournisseurs ont une valeur plus linéaire
            return base_value * 1.2
    
    def get_price_adjustment(self):
        """
        Calcule l'ajustement de prix offert par la coalition.
        
        Returns:
            float: Facteur d'ajustement (multiplicateur)
        """
        if self.type == "buyer":
            # Les acheteurs obtiennent des remises
            # Plus la valeur est élevée, plus la remise est grande
            discount = min(0.3, 0.05 + (self.value / 100) * 0.01)
            return 1 - discount
        else:
            # Les fournisseurs peuvent augmenter leurs prix minimums
            increase = min(0.2, 0.05 + (self.value / 100) * 0.01)
            return 1 + increase


def idp_coalition_formation(agents, max_coalition_size=None):
    """
    Algorithme IDP (Improved Dynamic Programming) pour former des coalitions optimales.
    
    Args:
        agents (list): Liste des agents
        max_coalition_size (int, optional): Taille maximale d'une coalition
        
    Returns:
        list: Liste des coalitions formées
    """
    if not agents:
        return []
    
    # Si la taille maximale n'est pas spécifiée, utiliser le nombre d'agents
    if max_coalition_size is None:
        max_coalition_size = len(agents)
    
    # Vérifier le type des agents
    agent_type = agents[0].type
    
    # Tableau pour stocker les meilleures structures de coalition
    dp = [[] for _ in range(len(agents) + 1)]
    dp[0] = []  # Cas de base: 0 agent
    
    # Pour chaque nombre d'agents
    for i in range(1, len(agents) + 1):
        best_value = 0
        best_structure = []
        
        # Essayer toutes les tailles possibles pour la dernière coalition
        for j in range(1, min(i, max_coalition_size) + 1):
            # Créer une coalition avec les j derniers agents
            last_coalition = Coalition(agents[i-j:i], agent_type)
            
            # Valeur totale = valeur de la dernière coalition + valeur optimale pour les agents restants
            value = last_coalition.value
            if i-j > 0:
                value += sum(c.value for c in dp[i-j])
            
            # Mettre à jour la meilleure structure si nécessaire
            if value > best_value:
                best_value = value
                best_structure = dp[i-j] + [last_coalition]
        
        dp[i] = best_structure
    
    return dp[len(agents)]


def token_based_coalition_formation(agents, max_iterations=10):
    """
    Algorithme basé sur des jetons pour former des coalitions de manière distribuée.
    
    Args:
        agents (list): Liste des agents
        max_iterations (int): Nombre maximum d'itérations
        
    Returns:
        list: Liste des coalitions formées
    """
    if not agents:
        return []
    
    # Vérifier le type des agents
    agent_type = agents[0].type