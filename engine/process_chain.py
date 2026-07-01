from typing import Dict, Any, List, Tuple
from .selection import select_best_modules_for_operation
from .kpi import compute_kpis
from .rules import apply_rules

def _pick_best_with_fallback(
    ranked_modules: List[Dict[str, Any]],
    current_total_cost: float,
    budget_max: float
) -> Tuple[Dict[str, Any], str]:
    """
    Try modules in rank order until one fits within the remaining budget.
    If none fit, return the cheapest module with a fallback note.
    """
    if not ranked_modules:
        return None, "NO_MODULE_FOUND"

    for candidate in ranked_modules:
        projected_cost = current_total_cost + candidate["total_cost"]
        if projected_cost <= budget_max:
            return candidate, "SELECTED"

    # None fit — pick the cheapest to minimize overrun
    cheapest = min(ranked_modules, key=lambda m: m["total_cost"])
    return cheapest, "FALLBACK_SELECTED"

def generate_process_chain(
    requirements: Dict[str, Any],
    product: Dict[str, Any],
    modules_db: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    """
    Generate the full process chain with module selection.
    Includes fallback logic: if the top-ranked module exceeds budget,
    the engine tries the next best one. If none fit, it selects the cheapest.
    Returns (process_chain, trace, kpis).
    """
    trace = []
    kpis = compute_kpis(requirements)
    trace.append(f"KPI: nominal_rate={kpis['nominal_rate_ppm']} ppm, takt_time={kpis['takt_time_s']} s")

    operations, rule_trace = apply_rules(requirements, product)
    trace.extend(rule_trace)

    process_chain = []
    running_total = 0.0
    budget_max = requirements.get("budget_max_eur", float('inf'))

    for op in operations:
        if not op.get("required", False):
            continue

        op_type = op["operation_type"]
        ranked_modules, sel_trace = select_best_modules_for_operation(
            modules_db, op_type, requirements, product, kpis["nominal_rate_ppm"]
        )
        trace.extend(sel_trace)

        if not ranked_modules:
            process_chain.append({
                "step": op["step"],
                "operation_type": op_type,
                "module": None,
                "parallel_units": 0,
                "status": "NO_MODULE_FOUND",
                "notes": op.get("notes", "")
            })
            trace.append(f"WARNING: No compatible module found for operation '{op_type}'.")
            continue

        best, status = _pick_best_with_fallback(ranked_modules, running_total, budget_max)
        running_total += best["total_cost"]

        process_chain.append({
            "step": op["step"],
            "operation_type": op_type,
            "module": {
                "id": best["id"],
                "name": best["name"],
                "category": best["category"],
                "capacity_ppm": best["capacity_ppm"],
                "cycle_time_s": best["cycle_time_s"],
                "parallel_units": best["parallel_units"],
                "total_cost": best["total_cost"],
                "total_footprint": best["total_footprint"],
                "total_energy": best["total_energy"],
                "score": best["score"]
            },
            "parallel_units": best["parallel_units"],
            "status": status,
            "notes": op.get("notes", "")
        })
        if status == "FALLBACK_SELECTED":
            trace.append(f"FALLBACK: {best['name']} (x{best['parallel_units']}) for '{op_type}' — top-ranked modules exceeded budget. Selected cheapest alternative.")
        else:
            trace.append(f"SELECTED: {best['name']} (x{best['parallel_units']}) for '{op_type}' with score={best['score']}")

    return process_chain, trace, kpis

def compute_line_architecture(process_chain: List[Dict[str, Any]], requirements: Dict[str, Any], kpis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine line architecture based on throughput, footprint, and variant constraints.
    Uses the NOMINAL rate (accounting for OEE and rejects) from pre-computed KPIs.
    """
    # Use pre-computed nominal rate from KPIs instead of recalculating
    nominal_rate = kpis.get("nominal_rate_ppm", 1)

    footprint_max = requirements.get("footprint_max_m2", 9999)
    variants = requirements.get("variants", 1)

    # Determine architecture type based on NOMINAL rate
    if nominal_rate >= 100:
        arch_type = "linear_transport_system"
        arch_name = "Linear Transport System (High Throughput)"
    elif nominal_rate >= 50:
        arch_type = "pallet_conveyor"
        arch_name = "Pallet Conveyor (Medium Throughput)"
    else:
        arch_type = "rotary_indexing_table"
        arch_name = "Rotary Indexing Table (Compact / Low Throughput)"

    # Override for high variant complexity
    if variants >= 5:
        arch_type = "hybrid_flexible"
        arch_name = "Hybrid Flexible System (Robot + Flexible Feeders)"

    # Override for low footprint
    total_footprint = sum(
        step["module"]["total_footprint"] for step in process_chain
        if step.get("module")
    )
    if total_footprint > footprint_max * 0.8 and arch_type != "rotary_indexing_table":
        arch_type = "rotary_indexing_table"
        arch_name = "Rotary Indexing Table (Footprint Optimized)"

    arch_reason = "Selected based on throughput and constraints."
    if variants >= 5:
        arch_reason = "High variant complexity requires hybrid flexible system with robot cells and flexible feeders."
    elif total_footprint > footprint_max * 0.8:
        arch_reason = "Footprint constraint triggered rotary indexing table selection for compact layout."
    elif nominal_rate >= 100:
        arch_reason = "High nominal throughput (>100 ppm) requires linear transport system for parallel processing."
    elif nominal_rate >= 50:
        arch_reason = "Medium nominal throughput (50-100 ppm) is optimal for pallet conveyor with buffer stations."
    else:
        arch_reason = "Low nominal throughput (<50 ppm) favors compact rotary indexing table for synchronous processing."

    return {
        "type": arch_type,
        "name": arch_name,
        "recommended_transport": arch_type,
        "reason": arch_reason,
        "total_footprint_m2": round(total_footprint, 2),
        "footprint_max_m2": footprint_max
    }
