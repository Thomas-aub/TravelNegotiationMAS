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
    
    def add_message(self, message):
        """
        Ajoute un message au tableau et notifie les observateurs.
        
        Args:
            message (Message): Le message à ajouter
        """
        print()
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
        Notifie tous les observateurs d'un changement dans une négociation.
        
        Args:
            id_negotiation (str): L'identifiant de la négociation mise à jour
        """
        
        with self.lock:
            for observer in self.observers:
                observer.notify(id_negotiation)