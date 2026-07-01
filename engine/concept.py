from typing import Dict, Any, List
from datetime import datetime, timezone
from .process_chain import generate_process_chain, compute_line_architecture
from .kpi import compute_kpis
from utils.i18n import t, get_i18n

__all__ = ["generate_concept_report", "report_to_markdown"]

def _build_feasibility(warnings_raw: list, total_cost: float, total_footprint: float,
                       requirements: dict, kpis: dict, process_chain: list) -> dict:
    """Single source of truth for feasibility checks."""
    warnings = []
    feasibility = "PASS"

    if total_cost > requirements["budget_max_eur"]:
        warnings.append({
            "type": "cost_overrun",
            "severity": "error",
            "message": f"Cost overrun: {total_cost} EUR > budget {requirements['budget_max_eur']} EUR"
        })
        feasibility = "FAIL"
    if total_footprint > requirements["footprint_max_m2"]:
        warnings.append({
            "type": "footprint_overrun",
            "severity": "error",
            "message": f"Footprint overrun: {total_footprint} m2 > max {requirements['footprint_max_m2']} m2"
        })
        feasibility = "FAIL"
    if any(step["status"] == "NO_MODULE_FOUND" for step in process_chain):
        warnings.append({
            "type": "no_module_found",
            "severity": "error",
            "message": "One or more operations have no compatible module."
        })
        feasibility = "FAIL"
    if kpis["capacity_utilization"] > 1.0:
        warnings.append({
            "type": "capacity_utilization_over",
            "severity": "error",
            "message": f"Capacity utilization is {kpis['capacity_utilization']*100:.1f}%. Annual demand exceeds line capacity. Cannot meet production target."
        })
        feasibility = "FAIL"
    elif kpis["capacity_utilization"] > 0.95:
        warnings.append({
            "type": "capacity_utilization_high",
            "severity": "warning",
            "message": "Capacity utilization > 95%. Consider dual-shift or rate increase."
        })
    if kpis["capacity_utilization"] < 0.3:
        warnings.append({
            "type": "capacity_utilization_low",
            "severity": "warning",
            "message": "Capacity utilization < 30%. Over-specified line."
        })
    
    # Add any raw trace warnings as advisory
    for w in warnings_raw:
        warnings.append({
            "type": "advisory",
            "severity": "warning",
            "message": w
        })
    
    return {"status": feasibility, "warnings": warnings}

def generate_concept_report(
    requirements: Dict[str, Any],
    product: Dict[str, Any],
    modules_db: List[Dict[str, Any]],
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Generate a complete concept report. Deterministic and reproducible.
    Creates a defensive copy of requirements to prevent caller-side mutation.
    """
    # Defensive copy: rules mutate requirements, so caller must be protected
    requirements = dict(requirements)
    
    process_chain, trace, kpis = generate_process_chain(requirements, product, modules_db)
    line_arch = compute_line_architecture(process_chain, requirements, kpis)

    total_cost = sum(
        step["module"]["total_cost"] for step in process_chain if step.get("module")
    )
    total_energy = sum(
        step["module"]["total_energy"] for step in process_chain if step.get("module")
    )
    total_footprint = line_arch["total_footprint_m2"]

    from .knowledge_model import KNOWLEDGE_MODEL

    # Generate recommendations from Knowledge Model
    report = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "engine": "deterministic_rule_based"
        },
        "input": requirements,
        "product": {
            "id": product["id"],
            "name": product["name"],
            "category": product["category"]
        },
        "kpis": kpis,
        "line_architecture": line_arch,
        "process_chain": process_chain,
        "cost_summary": {
            "total_cost_eur": round(total_cost, 2),
            "budget_max_eur": requirements["budget_max_eur"],
            "total_energy_kw": round(total_energy, 2),
            "total_footprint_m2": round(total_footprint, 2),
            "footprint_max_m2": requirements["footprint_max_m2"]
        },
        "feasibility": _build_feasibility([], total_cost, total_footprint, requirements, kpis, process_chain),
        "decision_trace": trace
    }

    recommendations = KNOWLEDGE_MODEL.get_all_recommendations_for_report(report, lang)
    # Deduplicate recommendations by type
    seen_types = set()
    deduplicated = []
    for rec in recommendations:
        if rec["type"] not in seen_types:
            seen_types.add(rec["type"])
            deduplicated.append(rec)
    report["recommendations"] = deduplicated

    return report

def report_to_markdown(report: Dict[str, Any]) -> str:
    """Convert concept report to Markdown using current i18n language."""
    lines = []
    lines.append(f"# Smart Machine Studio — {t('report_product')}")
    lines.append(f"\n**Generated:** {report['meta']['generated_at']}")
    lines.append(f"**Engine:** {report['meta']['engine']}")
    lines.append(f"**Version:** {report['meta']['version']}")

    lines.append(f"\n## {t('report_product')}")
    lines.append(f"- **{t('report_product')}:** {report['product']['name']}")
    lines.append(f"- **{t('report_category')}:** {report['product']['category']}")

    lines.append(f"\n## {t('report_kpis')}")
    lines.append(f"- **{t('kpi_nominal_rate_title')}:** {report['kpis']['nominal_rate_ppm']} ppm")
    lines.append(f"  *{t('kpi_nominal_rate_desc')}*")
    lines.append(f"- **{t('kpi_takt_time_title')}:** {report['kpis']['takt_time_s']} s")
    lines.append(f"  *{t('kpi_takt_time_desc')}*")
    lines.append(f"- **{t('kpi_annual_capacity_title')}:** {report['kpis']['annual_capacity']:,.0f} {t('kpi_unit_pcs')}")
    lines.append(f"  *{t('kpi_annual_capacity_desc')}*")
    lines.append(f"- **{t('kpi_utilization_title')}:** {report['kpis']['capacity_utilization']*100:.1f}%")
    lines.append(f"  *{t('kpi_utilization_desc')}*")
    lines.append(f"- **Target Output:** {report['kpis']['output_ppm']} ppm")
    lines.append(f"- **OEE Target:** {report['kpis']['oee_target']*100:.0f}%")
    lines.append(f"- **Reject Rate:** {report['kpis']['reject_rate']*100:.1f}%")

    lines.append(f"\n## {t('report_architecture')}")
    lines.append(f"- **{t('report_architecture')}:** {report['line_architecture'].get('name', 'N/A')}")
    lines.append(f"- **{t('report_architecture')} Reason:** {report['line_architecture'].get('reason', 'N/A')}")
    lines.append(f"- **Total Footprint:** {report['line_architecture'].get('total_footprint_m2', 'N/A')} m²")
    lines.append(f"- **Footprint Limit:** {report['line_architecture'].get('footprint_max_m2', 'N/A')} m²")

    lines.append(f"\n## {t('report_process_chain')}")
    for step in report["process_chain"]:
        lines.append(f"\n### Step {step['step']}: {step['operation_type'].upper()}")
        if step.get("module"):
            m = step["module"]
            lines.append(f"- **Module:** {m.get('name', 'N/A')} ({m.get('id', 'N/A')})")
            lines.append(f"- **Parallel Units:** {m.get('parallel_units', 'N/A')}")
            lines.append(f"- **Total Cost:** {m.get('total_cost', 'N/A')} EUR")
            lines.append(f"- **Total Footprint:** {m.get('total_footprint', 'N/A')} m2")
            lines.append(f"- **Score:** {m.get('score', 'N/A')}")
        else:
            lines.append(f"- **Status:** {step.get('status', 'N/A')} — {t('no_module')}")
        lines.append(f"- **Notes:** {step.get('notes', '')}")

    lines.append(f"\n## {t('report_cost_summary')}")
    for k, v in report.get("cost_summary", {}).items():
        lines.append(f"- **{k}:** {v}")

    lines.append(f"\n## {t('report_feasibility')}")
    lines.append(f"- **Status:** {report.get('feasibility', {}).get('status', 'N/A')}")
    raw_warnings = report.get("feasibility", {}).get("warnings", [])
    if raw_warnings:
        lines.append(f"- **{t('report_warnings')}:**")
        for w in raw_warnings:
            if isinstance(w, dict):
                lines.append(f"  - [{w.get('severity', 'warning').upper()}] {w.get('message', '')}")
            else:
                lines.append(f"  - {w}")
    else:
        lines.append(f"- **{t('report_warnings')}:** {t('report_none')}")

    lines.append(f"\n## {t('report_trace')}")
    for tr in report.get("decision_trace", []):
        lines.append(f"- {tr}")

    return "\n".join(lines)
