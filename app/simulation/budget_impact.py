from config.costs import COST_MODEL

def estimate_budget_impact(budget, actions):
    used_budget = 0
    total_impact = 0
    selected_actions = []

    for action, enabled in actions.items():
        if not enabled:
            continue

        cost = COST_MODEL[action]["cost"]
        impact = COST_MODEL[action]["impact"]

        if used_budget + cost <= budget:
            used_budget += cost
            total_impact += impact
            selected_actions.append(action)

    return used_budget, total_impact, selected_actions
