from typing import Dict, Any, List
from datetime import datetime
from .process_chain import generate_process_chain, compute_line_architecture
from .kpi import compute_kpis
from utils.i18n import t, get_i18n

def generate_concept_report(
    requirements: Dict[str, Any],
    product: Dict[str, Any],
    modules_db: List[Dict[str, Any]],
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Generate a complete concept report. Deterministic and reproducible.
    """
    process_chain, trace, kpis = generate_process_chain(requirements, product, modules_db)
    line_arch = compute_line_architecture(process_chain, requirements)

    # Feasibility checks
    warnings = []
    feasibility = "PASS"

    total_cost = sum(
        step["module"]["total_cost"] for step in process_chain if step.get("module")
    )
    total_energy = sum(
        step["module"]["total_energy"] for step in process_chain if step.get("module")
    )
    total_footprint = line_arch["total_footprint_m2"]

    if total_cost > requirements["budget_max_eur"]:
        warnings.append(f"Cost overrun: {total_cost} EUR > budget {requirements['budget_max_eur']} EUR")
        feasibility = "FAIL"
    if total_footprint > requirements["footprint_max_m2"]:
        warnings.append(f"Footprint overrun: {total_footprint} m2 > max {requirements['footprint_max_m2']} m2")
        feasibility = "FAIL"
    if any(step["status"] == "NO_MODULE_FOUND" for step in process_chain):
        warnings.append("One or more operations have no compatible module.")
        feasibility = "FAIL"
    if kpis["capacity_utilization"] > 1.0:
        warnings.append(f"Capacity utilization is {kpis['capacity_utilization']*100:.1f}%. Annual demand exceeds line capacity. Cannot meet production target.")
        feasibility = "FAIL"
    elif kpis["capacity_utilization"] > 0.95:
        warnings.append("Capacity utilization > 95%. Consider dual-shift or rate increase.")
    if kpis["capacity_utilization"] < 0.3:
        warnings.append("Capacity utilization < 30%. Over-specified line.")

    from .knowledge_model import KNOWLEDGE_MODEL

    # Generate recommendations from Knowledge Model
    report = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
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
        "feasibility": {
            "status": feasibility,
            "warnings": warnings
        },
        "decision_trace": trace
    }

    recommendations = KNOWLEDGE_MODEL.get_all_recommendations_for_report(report, lang)
    report["recommendations"] = recommendations

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
    lines.append(f"- **{t('report_architecture')}:** {report['line_architecture']['name']}")
    lines.append(f"- **{t('report_architecture')} Reason:** {report['line_architecture'].get('reason', 'N/A')}")
    lines.append(f"- **Total Footprint:** {report['line_architecture']['total_footprint_m2']} m²")
    lines.append(f"- **Footprint Limit:** {report['line_architecture']['footprint_max_m2']} m²")

    lines.append(f"\n## {t('report_process_chain')}")
    for step in report["process_chain"]:
        lines.append(f"\n### Step {step['step']}: {step['operation_type'].upper()}")
        if step["module"]:
            m = step["module"]
            lines.append(f"- **Module:** {m['name']} ({m['id']})")
            lines.append(f"- **Parallel Units:** {m['parallel_units']}")
            lines.append(f"- **Total Cost:** {m['total_cost']} EUR")
            lines.append(f"- **Total Footprint:** {m['total_footprint']} m2")
            lines.append(f"- **Score:** {m['score']}")
        else:
            lines.append(f"- **Status:** {step['status']} — {t('no_module')}")
        lines.append(f"- **Notes:** {step['notes']}")

    lines.append(f"\n## {t('report_cost_summary')}")
    for k, v in report["cost_summary"].items():
        lines.append(f"- **{k}:** {v}")

    lines.append(f"\n## {t('report_feasibility')}")
    lines.append(f"- **Status:** {report['feasibility']['status']}")
    if report["feasibility"]["warnings"]:
        lines.append(f"- **{t('report_warnings')}:**")
        for w in report["feasibility"]["warnings"]:
            lines.append(f"  - {w}")
    else:
        lines.append(f"- **{t('report_warnings')}:** {t('report_none')}")

    lines.append(f"\n## {t('report_trace')}")
    for tr in report["decision_trace"]:
        lines.append(f"- {tr}")

    return "\n".join(lines)
