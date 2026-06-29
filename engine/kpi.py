from math import ceil
from typing import Dict, Any

# KPI Engine — Single Source of Truth

def compute_nominal_rate(output_ppm: float, oee: float, reject_rate: float) -> float:
    """Nominal production rate required to achieve target output given OEE and reject rate."""
    if oee <= 0 or oee > 1:
        raise ValueError("OEE must be in (0, 1]")
    if reject_rate < 0 or reject_rate >= 1:
        raise ValueError("Reject rate must be in [0, 1)")
    return output_ppm / (oee * (1 - reject_rate))

def compute_takt_time(nominal_rate_ppm: float) -> float:
    """Takt time in seconds per part."""
    if nominal_rate_ppm <= 0:
        raise ValueError("Nominal rate must be > 0")
    return 60.0 / nominal_rate_ppm

def compute_kpis(requirements: Dict[str, Any]) -> Dict[str, float]:
    """Deterministic KPI computation from customer requirements."""
    output_ppm = requirements["output_ppm"]
    oee = requirements["oee_target"]
    reject_rate = requirements["reject_rate"]

    nominal_rate = compute_nominal_rate(output_ppm, oee, reject_rate)
    takt_time = compute_takt_time(nominal_rate)

    # Annual capacity check
    annual_capacity = nominal_rate * 60 * 16 * 250  # 2-shift, 250 days/year
    annual_demand = requirements["annual_demand"]
    capacity_utilization = annual_demand / annual_capacity if annual_capacity > 0 else 0.0

    return {
        "nominal_rate_ppm": round(nominal_rate, 4),
        "takt_time_s": round(takt_time, 4),
        "annual_capacity": round(annual_capacity, 0),
        "capacity_utilization": round(capacity_utilization, 4),
        "output_ppm": output_ppm,
        "oee_target": oee,
        "reject_rate": reject_rate,
    }

def compute_parallel_units(nominal_rate_ppm: float, module_capacity_ppm: float) -> int:
    """Compute required number of parallel modules."""
    if module_capacity_ppm <= 0:
        raise ValueError("Module capacity must be > 0")
    return ceil(nominal_rate_ppm / module_capacity_ppm)
