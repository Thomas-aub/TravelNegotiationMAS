from agent import Agent
import strategies
import time

class BuyerCoalition(Agent):
    def __init__(self, coalition_id, message_board, members):
        super().__init__(coalition_id, "buyer", message_board)
        self.members = members
        self.negotiations_to_process = set()

        self.max_price = max(member.max_price for member in members)
        self.first_price = min(getattr(member, 'current_price', member.max_price * 0.5) for member in members)
        self.current_price = self.first_price

        self.favourite_companies = list(set().union(*(m.favourite_companies for m in members)))
        self.worst_companies = list(set().union(*(m.worst_companies for m in members)))
        self.blocked_companies = list(set().union(*(m.blocked_companies or [] for m in members)))

        self.strategy_type = "default"
        if any(m.strategy_type == "aggressive" for m in members):
            self.strategy_type = "aggressive"

        self.coalition_value = self.calculate_value()

    def calculate_value(self):
        base_value = len(self.members) * 10
        return base_value * (1 + 0.05 * len(self.members))

    def notify(self, id_negotiation):
        if (self.message_board.is_participant(id_negotiation, self.id) or
            not self.message_board.has_buyer_participant(id_negotiation)):
            self.negotiations_to_process.add(id_negotiation)

    def run(self):
        while self.running:
            for id_neg in list(self.negotiations_to_process):
                self.handle_negotiation(id_neg)
                self.negotiations_to_process.remove(id_neg)
            time.sleep(0.1)

    def handle_negotiation(self, id_negotiation):
        msg = self.message_board.get_last_message(id_negotiation)
        if not msg or msg.type != "supplier":
            return

        if id_negotiation not in self.active_negotiations:
            self.message_board.register_participant(id_negotiation, self.id)
            self.active_negotiations[id_negotiation] = -1

        if not self.process_message(msg):
            return

        if self.strategy_type == "default":
            price, state = strategies.buyer_default_strategy(
                self.current_price, self.max_price, msg.price,
                self.favourite_companies, self.worst_companies, self.blocked_companies, msg.company
            )
        else:
            price, state = strategies.buyer_aggressive_strategy(
                self.current_price, self.max_price, msg.price,
                self.favourite_companies, self.worst_companies, self.blocked_companies, msg.company
            )

        self.send_message(id_negotiation, price, state)
        if state == "processing":
            self.current_price = price