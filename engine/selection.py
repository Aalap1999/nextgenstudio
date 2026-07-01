from typing import Dict, Any, List, Tuple
from math import ceil
from copy import deepcopy
from .kpi import compute_parallel_units
from .knowledge_model import KNOWLEDGE_MODEL

def stage_hard_filter(
    modules: List[Dict[str, Any]],
    requirements: Dict[str, Any],
    product: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Stage 1: Hard filter based on capability, industry, cleanroom, tolerance, and variant constraints.
    """
    trace = []
    filtered = []

    for mod in modules:
        # Industry compatibility
        if product["category"] not in mod["supported_industries"]:
            continue

        # Cleanroom compatibility
        if requirements.get("cleanroom_required") and not mod.get("cleanroom_compatible", False):
            continue

        # Tolerance compatibility (skip if module has no tolerance constraint)
        module_tolerance = mod.get("tolerance_um", 9999)
        if module_tolerance < 9999 and requirements["tolerance_um"] < module_tolerance:
            continue

        # Variant flexibility
        if requirements["variants"] > 1 and mod.get("variant_flexibility", 0) < 2:
            continue

        filtered.append(mod)

    trace.append(f"STAGE1_HARD_FILTER: {len(filtered)}/{len(modules)} modules passed.")
    return filtered, trace

def stage_capacity_model(
    modules: List[Dict[str, Any]],
    nominal_rate_ppm: float
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Stage 2: Compute parallel units for each module.
    Operates on copies — never mutates the original module dicts.
    """
    trace = []
    for mod in modules:
        mod["parallel_units"] = compute_parallel_units(nominal_rate_ppm, mod["capacity_ppm"])
        mod["total_footprint"] = mod["parallel_units"] * mod["footprint_m2"]
        mod["total_cost"] = mod["parallel_units"] * mod["cost_eur"]
        mod["total_energy"] = mod["parallel_units"] * mod["energy_kw"]

    trace.append(f"STAGE2_CAPACITY: Computed parallel units for {len(modules)} modules at nominal_rate={nominal_rate_ppm} ppm.")
    return modules, trace

def stage_scoring(
    modules: List[Dict[str, Any]],
    optimization_priority: str
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Stage 3: Score modules based on optimization priority using knowledge model weights.
    """
    trace = []
    if not modules:
        return [], trace

    weights = KNOWLEDGE_MODEL.get_optimization_weights(optimization_priority)

    # Normalize metrics (lower is better for cost, footprint, energy; higher is better for flexibility)
    costs = [m["total_cost"] for m in modules]
    footprints = [m["total_footprint"] for m in modules]
    energies = [m["total_energy"] for m in modules]
    flexibilities = [m["flexibility_score"] for m in modules]

    min_cost, max_cost = min(costs), max(costs)
    min_fp, max_fp = min(footprints), max(footprints)
    min_en, max_en = min(energies), max(energies)
    min_flex, max_flex = min(flexibilities), max(flexibilities)

    def norm_cost(v):
        return (v - min_cost) / (max_cost - min_cost) if max_cost > min_cost else 0.0
    def norm_fp(v):
        return (v - min_fp) / (max_fp - min_fp) if max_fp > min_fp else 0.0
    def norm_en(v):
        return (v - min_en) / (max_en - min_en) if max_en > min_en else 0.0
    def norm_flex(v):
        return (v - min_flex) / (max_flex - min_flex) if max_flex > min_flex else 0.0

    for mod in modules:
        c = norm_cost(mod["total_cost"])
        f = norm_fp(mod["total_footprint"])
        e = norm_en(mod["total_energy"])
        fl = norm_flex(mod["flexibility_score"])

        score = (
            weights["cost"] * c +
            weights["footprint"] * f +
            weights["energy"] * e +
            weights["flexibility"] * (1 - fl)
        )

        mod["score"] = round(score, 4)

    modules.sort(key=lambda x: x["score"])
    trace.append(f"STAGE3_SCORING: Sorted {len(modules)} modules by priority '{optimization_priority}' (weights: {weights}).")
    return modules, trace

def select_best_modules_for_operation(
    modules_db: List[Dict[str, Any]],
    operation_type: str,
    requirements: Dict[str, Any],
    product: Dict[str, Any],
    nominal_rate_ppm: float
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Full 3-stage pipeline for a single operation type.
    Returns (ranked_modules, trace).
    CRITICAL: Deep-copies modules before processing to avoid mutating the original database.
    """
    trace = []

    # Use knowledge model for capability mapping
    target_tags = KNOWLEDGE_MODEL.get_capability_tags(operation_type)
    matching = [m for m in modules_db if any(tag in m["capability_tags"] for tag in target_tags)]
    trace.append(f"OPERATION '{operation_type}': {len(matching)} modules match capability tags {target_tags}.")

    if not matching:
        return [], trace

    # Deep copy to prevent mutation of the original module database
    matching_copies = [deepcopy(m) for m in matching]

    # Stage 1: Hard filter
    filtered, t1 = stage_hard_filter(matching_copies, requirements, product)
    trace.extend(t1)
    if not filtered:
        return [], trace

    # Stage 2: Capacity
    capacity_applied, t2 = stage_capacity_model(filtered, nominal_rate_ppm)
    trace.extend(t2)

    # Stage 3: Scoring
    scored, t3 = stage_scoring(capacity_applied, requirements["optimization_priority"])
    trace.extend(t3)

    return scored, trace
