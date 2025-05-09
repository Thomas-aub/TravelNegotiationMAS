import random
from buyerCoalition import BuyerCoalition
from supplierCoalition import SupplierCoalition

def form_buyer_coalitions(buyers, max_coalition_size=3):
    coalitions = []
    remaining_buyers = buyers.copy()

    remaining_buyers.sort(key=lambda b: b.max_price, reverse=True)

    while len(remaining_buyers) >= 2:
        coalition_members = remaining_buyers[:max_coalition_size]
        coalition_id = f"Coalition_B_{len(coalitions) + 1}"
        new_coalition = BuyerCoalition(coalition_id, coalition_members[0].message_board, coalition_members)
        coalitions.append(new_coalition)
        remaining_buyers = remaining_buyers[max_coalition_size:]

    return coalitions, remaining_buyers

def form_supplier_coalitions(suppliers, max_coalition_size=3):
    coalitions = []
    remaining_suppliers = suppliers.copy()

    remaining_suppliers.sort(key=lambda s: s.min_price)

    while len(remaining_suppliers) >= 2:
        coalition_members = remaining_suppliers[:max_coalition_size]
        coalition_id = f"Coalition_S_{len(coalitions) + 1}"
        new_coalition = SupplierCoalition(coalition_id, coalition_members[0].message_board, coalition_members)
        coalitions.append(new_coalition)
        remaining_suppliers = remaining_suppliers[max_coalition_size:]

    return coalitions, remaining_suppliers

def idp_coalition_formation(agents, agent_type, max_coalition_size=None):
    if not agents:
        return []

    if max_coalition_size is None:
        max_coalition_size = len(agents)

    dp = [[] for _ in range(len(agents) + 1)]
    dp[0] = []

    for i in range(1, len(agents) + 1):
        best_value = 0
        best_structure = []

        for j in range(1, min(i, max_coalition_size) + 1):
            last_agents = agents[i - j:i]

            if j > 1:
                coalition_id = f"Coalition_{'_'.join([a.id for a in last_agents])}"
                if agent_type == "buyer":
                    last_coalition = BuyerCoalition(coalition_id, last_agents[0].message_board, last_agents)
                else:
                    last_coalition = SupplierCoalition(coalition_id, last_agents[0].message_board, last_agents)
                value = last_coalition.coalition_value
            else:
                last_coalition = last_agents[0]
                value = 0

            if i - j > 0:
                value += sum(getattr(c, 'coalition_value', 0) for c in dp[i - j])

            if value > best_value:
                best_value = value
                if j > 1:
                    best_structure = dp[i - j] + [last_coalition]
                else:
                    best_structure = dp[i - j] + last_agents

        dp[i] = best_structure

    return dp[len(agents)]

def token_based_coalition_formation(agents, agent_type, max_iterations=10):
    if not agents:
        return []

    coalitions = []
    used_pairs = set()

    for _ in range(max_iterations):
        random.shuffle(agents)
        for i in range(len(agents) - 1):
            a1, a2 = agents[i], agents[i + 1]
            pair = tuple(sorted([a1.id, a2.id]))
            if pair not in used_pairs:
                coalition_id = f"Coalition_{'_'.join([a1.id, a2.id])}"
                if agent_type == "buyer":
                    new_coalition = BuyerCoalition(coalition_id, a1.message_board, [a1, a2])
                else:
                    new_coalition = SupplierCoalition(coalition_id, a1.message_board, [a1, a2])
                coalitions.append(new_coalition)
                used_pairs.add(pair)

    return coalitions