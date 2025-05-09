from agent import Agent
import strategies
import time

class SupplierCoalition(Agent):
    def __init__(self, coalition_id, message_board, members):
        super().__init__(coalition_id, "supplier", message_board)
        self.members = members
        self.negotiations_to_process = set()

        self.coalition_value = self.calculate_value()
        self.min_price = sum(member.min_price for member in members) / len(members)
        self.first_price = max(member.min_price * 1.5 for member in members)
        self.current_price = self.first_price
        self.ticket_remaining = sum(member.ticket_remaining for member in members)
        self.company = f"Coalition-{'-'.join([member.company for member in members])}"
        self.strategy_type = "default"
        if any(member.strategy_type == "conciliatory" for member in members):
            self.strategy_type = "conciliatory"

    def calculate_value(self):
        base_value = len(self.members) * 15
        price_range = max(member.min_price for member in self.members) - min(member.min_price for member in self.members)
        diversity_factor = 1 + (price_range / 1000)
        strategies_count = len(set(member.strategy_type for member in self.members))
        strategy_factor = 1 + (strategies_count / len(self.members)) * 0.2
        return base_value * diversity_factor * strategy_factor

    def notify(self, id_negotiation):
        self.negotiations_to_process.add(id_negotiation)

    def run(self):
        while self.running:
            negotiations = self.negotiations_to_process.copy()
            for id_negotiation in negotiations:
                self.handle_negotiation(id_negotiation)
                self.negotiations_to_process.remove(id_negotiation)
            time.sleep(0.1)

    def handle_negotiation(self, id_negotiation):
        last_message = self.message_board.get_last_message(id_negotiation)
        if not self.message_board.is_participant(id_negotiation, self.id):
            return
        if last_message.type != "buyer":
            return
        if not self.process_message(last_message):
            return

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
            print(f"Supplier Coalition {self.id} completed a sale at {response_price}")
            if self.ticket_remaining <= 0:
                print(f"Supplier Coalition {self.id} has no more tickets to sell.")

    def start_negotiation(self):
        """
        Démarre une nouvelle négociation.

        Returns:
            str: L'identifiant de la négociation créée
        """
        id_negotiation = self.message_board.get_next_negotiation_id()
        self.active_negotiations[id_negotiation] = -1
        self.message_board.register_participant(id_negotiation, self.id)
        self.send_message(id_negotiation, self.current_price)
        return id_negotiation