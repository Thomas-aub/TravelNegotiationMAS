import threading
import time
from collections import defaultdict

class SharedMessageBoard:
   
    def __init__(self):
        """
        Initialise le tableau de messages partagé avec un verrou pour l'accès thread-safe.
        """
        self.messages = defaultdict(list)  # Dictionnaire avec id_negotiation comme clé
        self.lock = threading.Lock()  # Verrou pour l'accès thread-safe
        self.observers = []  # Liste des agents observant le tableau
        self.negotiation_id_counter = 0  # Compteur pour les IDs de négociation
        self.negotiation_id_lock = threading.Lock()  # Verrou pour l'accès au compteur
        self.negotiation_participants = defaultdict(set)  # Participants par négociation

    def add_message(self, message):
        """
        Ajoute un message au tableau et notifie les observateurs.

        Args:
            message (Message): Le message à ajouter
        """
        with self.lock:
            self.messages[message.id_negotiation].append(message)
            self.messages[message.id_negotiation].sort(key=lambda m: m.message_number)
        self.notify_observers(message.id_negotiation)

    def get_last_message(self, id_negotiation):
        """
        Récupère le dernier message d'une négociation spécifique.

        Args:
            id_negotiation (str): L'identifiant de la négociation

        Returns:
            Message: Le dernier message ou None si aucun message n'existe
        """
        with self.lock:
            messages = self.messages.get(id_negotiation, [])
            return messages[-1] if messages else None

    def get_all_messages(self, id_negotiation):
        """
        Récupère tous les messages d'une négociation spécifique.

        Args:
            id_negotiation (str): L'identifiant de la négociation

        Returns:
            list: Liste des messages
        """
        with self.lock:
            return self.messages.get(id_negotiation, [])[:]

    def register_observer(self, observer):
        """
        Enregistre un agent comme observateur du tableau.

        Args:
            observer: L'agent à enregistrer
        """
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_observers(self, id_negotiation):
        """
        Notifie les observateurs d'un changement.
        Chaque observateur est responsable de déterminer s'il doit traiter le message.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation mise à jour
        """
        for observer in self.observers:
            observer.notify(id_negotiation)

    def get_next_negotiation_id(self):
        """
        Obtient l'ID suivant pour une nouvelle négociation de manière thread-safe.

        Returns:
            int: L'ID unique pour la nouvelle négociation
        """
        with self.negotiation_id_lock:
            self.negotiation_id_counter += 1
            return self.negotiation_id_counter

    def register_participant(self, id_negotiation, agent_id):
        """
        Enregistre un agent comme participant à une négociation.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation
            agent_id (str): L'identifiant de l'agent
        """
        with self.lock:
            self.negotiation_participants[id_negotiation].add(agent_id)

    def is_participant(self, id_negotiation, agent_id):
        """
        Vérifie si un agent est participant à une négociation.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation
            agent_id (str): L'identifiant de l'agent
            
        Returns:
            bool: True si l'agent est participant, False sinon
        """
        with self.lock:
            return agent_id in self.negotiation_participants[id_negotiation]

    def get_negotiation_participants(self, id_negotiation):
        """
        Récupère tous les participants à une négociation.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation
            
        Returns:
            set: Ensemble des identifiants des agents participants
        """
        with self.lock:
            return self.negotiation_participants.get(id_negotiation, set()).copy()

    def has_buyer_participant(self, id_negotiation):
        """
        Vérifie si une négociation a déjà un acheteur participant.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation
            
        Returns:
            bool: True s'il y a déjà un acheteur participant, False sinon
        """
        with self.lock:
            participants = self.negotiation_participants.get(id_negotiation, set())
            return any(p.startswith('B_') or p.startswith('buyer_') for p in participants)