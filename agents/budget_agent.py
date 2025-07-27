def evaluate_budget(pois, total_distance_km, budget_usd, cost_per_poi=5, cost_per_km=0.15):
    num_pois = len(pois)
    poi_cost = num_pois * cost_per_poi
    travel_cost = total_distance_km * cost_per_km
    total_cost = poi_cost + travel_cost

    if total_cost > budget_usd:
        affordable_pois = int((budget_usd - (total_distance_km * cost_per_km)) // cost_per_poi)
        affordable_pois = max(1, min(affordable_pois, num_pois))
        return {
            "within_budget": False,
            "suggested_num_pois": affordable_pois,
            "estimated_cost": total_cost
        }
    else:
        return {
            "within_budget": True,
            "suggested_num_pois": len(pois),
            "estimated_cost": total_cost
        }
