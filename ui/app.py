import streamlit as st
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from utils.validator import (
    load_and_validate_modules, load_and_validate_products,
    validate_customer_requirements, ValidationError,
    load_json, _validate_module_item
)
from utils.i18n import I18n, set_language, t
from engine.concept import generate_concept_report, report_to_markdown
from engine.knowledge_model import KNOWLEDGE_MODEL


# ===================================================================
# HELPERS
# ===================================================================

def fmt_compact(n, decimals=0):
    """Format number with k/M suffix. 20000 -> 20k, 1500000 -> 1.5M"""
    if n is None:
        return "-"
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.{max(1, decimals)}f}M"
    elif abs(n) >= 1000:
        return f"{n / 1000:.{decimals}f}k"
    else:
        return f"{n:.{decimals}f}"


def get_module_data_path():
    return os.path.join(BASE_DIR, "data", "modules.json")


def write_module_to_db(new_module: dict) -> None:
    """Append a validated module to the modules.json file."""
    path = get_module_data_path()
    data = load_json(path)
    data["modules"].append(new_module)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_architecture_display_name(arch_type: str, lang: str) -> str:
    """Translate architecture type to localized display name."""
    mapping = {
        "linear_transport_system": {"en": "Linear Transport System (High Throughput)", "de": "Linear-Transportsystem (Hoher Durchsatz)"},
        "pallet_conveyor": {"en": "Pallet Conveyor (Medium Throughput)", "de": "Paletten-Foerderer (Mittlerer Durchsatz)"},
        "rotary_indexing_table": {"en": "Rotary Indexing Table (Compact / Low Throughput)", "de": "Rundtakt-Tisch (Kompakt / Niedriger Durchsatz)"},
        "hybrid_flexible": {"en": "Hybrid Flexible System (Robot + Flexible Feeders)", "de": "Hybrides Flexibles System (Roboter + Flexible Zufuehrer)"},
    }
    entry = mapping.get(arch_type, {})
    return entry.get(lang, entry.get("en", arch_type))


# ===================================================================
# SESSION STATE
# ===================================================================

def _init_state():
    """Initialize all session_state keys that are NOT widget-managed."""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "page" not in st.session_state:
        st.session_state.page = "Configurator"
    if "product_idx" not in st.session_state:
        st.session_state.product_idx = 0
    if "cleanroom_check" not in st.session_state:
        st.session_state.cleanroom_check = None
    if "_last_product_name" not in st.session_state:
        st.session_state._last_product_name = None


_init_state()
set_language(st.session_state.lang)

st.set_page_config(
    page_title="NextGen Smart Machine Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===================================================================
# HEADER
# ===================================================================

def render_header():
    col_main, col_btn = st.columns([6, 1])
    with col_main:
        st.title(t('header_title'))
        st.caption(t('header_subtitle'))
        st.caption(t('header_author'))
    with col_btn:
        st.markdown("&nbsp;", unsafe_allow_html=True)  # spacer
        btn_text = "DE" if st.session_state.lang == "en" else "EN"
        btn_help = t("language_switch")
        if st.button(btn_text, help=btn_help, use_container_width=True, key="lang_toggle"):
            st.session_state.lang = "de" if st.session_state.lang == "en" else "en"
            set_language(st.session_state.lang)


# ===================================================================
# SIDEBAR
# ===================================================================

def render_sidebar():
    page = st.session_state.get("page", "Configurator")

    if page == "Configurator":
        return _render_configurator_sidebar()
    else:
        return _render_library_sidebar()


def _render_configurator_sidebar():
    st.sidebar.markdown(f"### {t('sidebar_title')}")
    st.sidebar.caption(t('sidebar_description'))

    products_data = load_and_validate_products()
    product_names = {p["name"]: p for p in products_data["products"]}
    product_name_list = list(product_names.keys())

    # Product Section
    st.sidebar.markdown(f"**{t('section_product')}**")

    if st.session_state.product_idx >= len(product_name_list):
        st.session_state.product_idx = 0

    product_choice = st.sidebar.selectbox(
        t('product_label'), product_name_list,
        index=st.session_state.product_idx,
        help=t('product_help'), label_visibility="collapsed",
        key="product_choice"
    )
    new_idx = product_name_list.index(product_choice)
    if new_idx != st.session_state.product_idx:
        st.session_state.product_idx = new_idx

    selected_product = product_names[product_choice]

    if st.session_state._last_product_name != product_choice:
        st.session_state.cleanroom_check = selected_product["default_cleanroom_requirement"]
        st.session_state._last_product_name = product_choice

    cat_info = KNOWLEDGE_MODEL.get_product_category_info(selected_product["category"], st.session_state.lang)
    st.sidebar.caption(f"{t('category_label')}: {cat_info['description']}")
    st.sidebar.caption(f"{t('parts_label')}: {', '.join(selected_product['typical_parts_list'])}")
    st.sidebar.divider()

    # Production Section
    st.sidebar.markdown(f"**{t('section_production')}**")

    output_ppm = st.sidebar.number_input(
        t('output_rate_label'), min_value=0.1, value=60.0, step=5.0,
        help=t('output_rate_help'), key="output_ppm"
    )
    st.sidebar.caption(f"→ {fmt_compact(output_ppm)} {t('kpi_unit_ppm')}")

    annual_demand = st.sidebar.number_input(
        t('annual_demand_label'), min_value=1, value=500000, step=10000,
        help=t('annual_demand_help'), key="annual_demand"
    )
    st.sidebar.caption(f"→ {fmt_compact(annual_demand)} {t('kpi_unit_pcs')}")

    # OEE Slider (50-100) with normalized progress bar
    oee_min, oee_max = 50, 100
    oee_raw = st.sidebar.slider(
        t('oee_label'), oee_min, oee_max, 85, 1,
        help=t('oee_help'), key="oee_slider"
    )
    oee_pct = (oee_raw - oee_min) / (oee_max - oee_min)
    st.sidebar.progress(oee_pct, text=f"{oee_raw}%")

    # Reject Rate Slider (0-20) with normalized progress bar
    rej_min, rej_max = 0, 20
    reject_raw = st.sidebar.slider(
        t('reject_rate_label'), rej_min, rej_max, 2, 1,
        help=t('reject_rate_help'), key="reject_slider"
    )
    rej_pct = (reject_raw - rej_min) / (rej_max - rej_min)
    st.sidebar.progress(rej_pct, text=f"{reject_raw}%")

    st.sidebar.divider()

    # Quality Section
    st.sidebar.markdown(f"**{t('section_quality')}**")

    if st.session_state.cleanroom_check is None:
        st.session_state.cleanroom_check = selected_product["default_cleanroom_requirement"]

    cleanroom = st.sidebar.checkbox(
        t('cleanroom_label'), value=st.session_state.cleanroom_check,
        help=t('cleanroom_help'), key="cleanroom_check"
    )
    inspection = st.sidebar.checkbox(
        t('inspection_label'), value=True,
        help=t('inspection_help'), key="inspection_check"
    )
    traceability = st.sidebar.checkbox(
        t('traceability_label'), value=False,
        help=t('traceability_help'), key="traceability_check"
    )
    packaging = st.sidebar.checkbox(
        t('packaging_label'), value=True,
        help=t('packaging_help'), key="packaging_check"
    )
    tolerance_um = st.sidebar.number_input(
        t('tolerance_label'), min_value=0.1, value=100.0, step=1.0,
        help=t('tolerance_help'), key="tolerance_um"
    )
    st.sidebar.caption(f"→ {tolerance_um:.1f} um")

    st.sidebar.divider()

    # Constraints Section
    st.sidebar.markdown(f"**{t('section_constraints')}**")
    variants = st.sidebar.number_input(
        t('variants_label'), min_value=1, value=1, step=1,
        help=t('variants_help'), key="variants"
    )
    footprint_max = st.sidebar.number_input(
        t('footprint_label'), min_value=0.1, value=50.0, step=1.0,
        help=t('footprint_help'), key="footprint_max"
    )
    st.sidebar.caption(f"→ {footprint_max:.1f} m2")
    budget_max = st.sidebar.number_input(
        t('budget_label'), min_value=1000, value=500000, step=10000,
        help=t('budget_help'), key="budget_max"
    )
    st.sidebar.caption(f"→ {fmt_compact(budget_max)} EUR")

    # Custom validation - only show errors for truly invalid values
    errors = []
    if output_ppm <= 0:
        errors.append(("output_ppm", t("err_output_ppm_positive")))
    if annual_demand <= 0:
        errors.append(("annual_demand", t("err_annual_demand_positive")))
    if tolerance_um <= 0:
        errors.append(("tolerance_um", t("err_tolerance_positive")))
    if footprint_max <= 0:
        errors.append(("footprint_max", t("err_footprint_positive")))
    if budget_max <= 0:
        errors.append(("budget_max", t("err_budget_positive")))

    for field, msg in errors:
        st.sidebar.error(msg)

    st.sidebar.divider()

    # Optimization Section
    st.sidebar.markdown(f"**{t('section_optimization')}**")
    opt_options = ["cost", "footprint", "energy", "flexibility"]
    opt_labels = {k: t(f"opt_{k}") for k in opt_options}
    optimization = st.sidebar.selectbox(
        t('optimization_label'), opt_options,
        format_func=lambda x: opt_labels[x],
        help=t('optimization_help'), key="optimization"
    )
    opt_info = KNOWLEDGE_MODEL.get_optimization_info(optimization, st.session_state.lang)
    st.sidebar.caption(opt_info["description"])

    requirements = {
        "product_type": selected_product["id"],
        "output_ppm": output_ppm,
        "annual_demand": annual_demand,
        "oee_target": oee_raw / 100.0,
        "reject_rate": reject_raw / 100.0,
        "variants": variants,
        "tolerance_um": tolerance_um,
        "cleanroom_required": cleanroom,
        "inspection_required": inspection,
        "traceability_required": traceability,
        "packaging_required": packaging,
        "footprint_max_m2": footprint_max,
        "budget_max_eur": budget_max,
        "optimization_priority": optimization
    }

    generate = st.sidebar.button(
        t('generate_button'), type="primary",
        use_container_width=True, help=t('generate_help'),
        key="generate_btn", disabled=bool(errors)
    )

    return selected_product, requirements, generate


def _render_library_sidebar():
    """Show a brief info panel on the Library page sidebar."""
    st.sidebar.markdown(f"### {t('page_library')}")
    st.sidebar.caption(t('library_description'))
    st.sidebar.divider()
    st.sidebar.info(t('library_add_description'))
    return None, None, None


# ===================================================================
# FOOTER NAVIGATION (bottom of main content)
# ===================================================================

def render_footer_nav():
    """Developer navigation at the bottom of the main content area."""
    page = st.session_state.get("page", "Configurator")

    st.divider()
    st.caption(t("page_nav_label"))

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        pass
    with c2:
        if st.button(
            t("page_configurator"),
            type="primary" if page == "Configurator" else "secondary",
            use_container_width=True,
            key="nav_configurator"
        ):
            if page != "Configurator":
                st.session_state.page = "Configurator"
                st.rerun()
    with c3:
        if st.button(
            t("page_library"),
            type="primary" if page == "Component Library" else "secondary",
            use_container_width=True,
            key="nav_library"
        ):
            if page != "Component Library":
                st.session_state.page = "Component Library"
                st.rerun()


# ===================================================================
# WELCOME PAGE
# ===================================================================

def render_welcome():
    st.info(f"**{t('welcome_title')}**  \n{t('welcome_text')}")

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown(f"### 1. {t('step1_title')}")
            st.write(t('step1_text'))
    with c2:
        with st.container(border=True):
            st.markdown(f"### 2. {t('step2_title')}")
            st.write(t('step2_text'))
    with c3:
        with st.container(border=True):
            st.markdown(f"### 3. {t('step3_title')}")
            st.write(t('step3_text'))

    st.divider()
    st.success(f"**{t('how_it_works_title')}**  \n{t('how_it_works_text')}")


# ===================================================================
# DASHBOARD
# ===================================================================

def render_kpi_dashboard(kpis, feasibility):
    st.subheader(t('kpi_section_title'))
    st.caption(t('kpi_section_caption'))

    status = feasibility["status"]
    util = kpis['capacity_utilization'] * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(
            label=t('kpi_nominal_rate_title'),
            value=f"{kpis['nominal_rate_ppm']:.2f} {t('kpi_unit_ppm')}",
            help=t('kpi_nominal_rate_desc')
        )
    with c2:
        st.metric(
            label=t('kpi_takt_time_title'),
            value=f"{kpis['takt_time_s']:.3f} {t('kpi_unit_seconds')}",
            help=t('kpi_takt_time_desc')
        )
    with c3:
        st.metric(
            label=t('kpi_annual_capacity_title'),
            value=f"{fmt_compact(kpis['annual_capacity'])} {t('kpi_unit_pcs')}",
            help=t('kpi_annual_capacity_desc')
        )
    with c4:
        delta_color = "normal" if 30 <= util <= 85 else "inverse"
        st.metric(
            label=t('kpi_utilization_title'),
            value=f"{util:.1f} {t('kpi_unit_percent')}",
            delta=None,
            help=t('kpi_utilization_desc')
        )
    with c5:
        st.metric(
            label=t('kpi_feasibility_title'),
            value=t(f'status_{status.lower()}'),
            help=t('kpi_feasibility_desc')
        )


def render_architecture(line_arch, cost):
    st.subheader(t('arch_section_title'))

    arch_name = get_architecture_display_name(line_arch.get("type", ""), st.session_state.lang)
    if not arch_name:
        arch_name = line_arch.get('name', '')

    st.write(f"**{arch_name}**")
    st.write(line_arch.get('reason', ''))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t('arch_footprint_metric'), f"{cost['total_footprint_m2']:.1f} / {cost['footprint_max_m2']:.0f} m2")
    with c2:
        st.metric(t('arch_cost_metric'), f"{fmt_compact(cost['total_cost_eur'])} / {fmt_compact(cost['budget_max_eur'])} EUR")
    with c3:
        st.metric(t('arch_energy_metric'), f"{cost['total_energy_kw']:.2f} kW")
    with c4:
        st.metric(t('arch_transport_metric'), line_arch.get('recommended_transport', '').replace('_', ' ').title())


def render_process_chain(process_chain):
    st.subheader(t('process_section_title'))
    st.caption(t('process_section_caption'))

    # Pipeline visualization using columns with arrows
    total_steps = len(process_chain)
    if total_steps > 0:
        cols = st.columns(total_steps * 2 - 1)  # step + arrow for each gap
        col_idx = 0
        for i, step in enumerate(process_chain):
            mod = step.get("module")
            if mod:
                module_name = mod["name"]
                units = f"x{mod['parallel_units']}"
                status = "✅"
            else:
                module_name = t('no_module')
                units = ""
                status = "❌"

            op_info = KNOWLEDGE_MODEL.get_operation_info(step["operation_type"], st.session_state.lang)
            op_name = op_info.get("name", step["operation_type"].replace("_", " ").upper()).upper()

            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{step['step']}** {status}")
                    st.caption(op_name)
                    st.write(f"**{module_name}**")
                    if units:
                        st.caption(units)
            col_idx += 1

            if i < total_steps - 1:
                with cols[col_idx]:
                    st.markdown("<div style='text-align:center; padding-top:30px; font-size:24px;'>➜</div>", unsafe_allow_html=True)
                col_idx += 1

    st.markdown(f"**{t('process_table_title')}**")
    table_data = []
    for step in process_chain:
        op_info = KNOWLEDGE_MODEL.get_operation_info(step["operation_type"], st.session_state.lang)
        op_name = op_info.get("name", step["operation_type"].replace("_", " ").title())
        if step["module"]:
            m = step["module"]
            table_data.append({
                t('col_step'): step["step"],
                t('col_operation'): op_name,
                t('col_module'): m["name"],
                t('col_units'): m["parallel_units"],
                t('col_unit_cost'): f"{fmt_compact(m['total_cost'] / max(m['parallel_units'], 1))} EUR",
                t('col_total_cost'): f"{fmt_compact(m['total_cost'])} EUR",
                t('col_footprint'): f"{m['total_footprint']:.2f} m2",
                t('col_score'): m["score"],
            })
        else:
            table_data.append({
                t('col_step'): step["step"],
                t('col_operation'): op_name,
                t('col_module'): t('no_module'),
                t('col_units'): 0,
                t('col_unit_cost'): "-",
                t('col_total_cost'): "-",
                t('col_footprint'): "-",
                t('col_score'): "-",
            })

    st.dataframe(table_data, use_container_width=True, hide_index=True)


def render_warnings(feasibility):
    if not feasibility["warnings"]:
        return
    st.subheader(t('warnings_title'))
    for w in feasibility["warnings"]:
        if "overrun" in w.lower() or "exceed" in w.lower() or "budget" in w.lower() or "footprint" in w.lower():
            st.error(w)
        else:
            st.warning(w)


def render_recommendations(recommendations):
    if not recommendations:
        return
    st.subheader(t('recommendations_title'))
    st.caption(t('recommendations_caption'))

    for rec in recommendations:
        severity = rec.get("severity", "warning")
        title = rec.get(f"title_{st.session_state.lang}", rec.get("title_en", ""))
        message = rec.get(f"message_{st.session_state.lang}", rec.get("message_en", ""))
        actions = rec.get("actions", [])

        if severity == "error":
            icon = "🔴"
        else:
            icon = "🟡"

        with st.container(border=True):
            st.markdown(f"{icon} **{title}** | {t(f'rec_severity_{severity}')}")
            st.write(message)
            if actions:
                st.write("**Actions:**")
                for action in actions:
                    st.write(f"- {action}")


def render_trace(trace):
    st.subheader(t('trace_title'))
    st.caption(t('trace_caption'))

    formatted_lines = []
    for line in trace:
        if line.startswith("KPI:"):
            formatted_lines.append(f"[KPI] {line}")
        elif line.startswith("STAGE1"):
            formatted_lines.append(f"[FILTER] {line}")
        elif line.startswith("STAGE2"):
            formatted_lines.append(f"[CAPACITY] {line}")
        elif line.startswith("STAGE3"):
            formatted_lines.append(f"[SCORE] {line}")
        elif line.startswith("SELECTED"):
            formatted_lines.append(f"  OK {line}")
        elif line.startswith("WARNING") or "NO MODULE" in line:
            formatted_lines.append(f"  ALERT {line}")
        elif line.startswith(("PRODUCT_RULE", "CUSTOMER_RULE", "TRACEABILITY_RULE", "INSPECTION_RULE", "TESTING_RULE", "PACKAGING_RULE", "CLEANROOM_RULE", "GLOBAL_RULE")):
            formatted_lines.append(f"  RULE {line}")
        else:
            formatted_lines.append(line)

    with st.expander("View Decision Trace"):
        st.code("\n".join(formatted_lines), language=None)


def render_export(report):
    st.subheader(t('export_title'))
    c1, c2 = st.columns(2)
    with c1:
        json_data = json.dumps(report, indent=2, ensure_ascii=False)
        st.download_button(
            label=t('export_json'), data=json_data,
            file_name="smart_machine_concept.json",
            mime="application/json", use_container_width=True
        )
    with c2:
        md_data = report_to_markdown(report)
        st.download_button(
            label=t('export_md'), data=md_data,
            file_name="smart_machine_concept.md",
            mime="text/markdown", use_container_width=True
        )
    st.caption(t('export_json_caption'))


def render_dashboard(report):
    render_kpi_dashboard(report["kpis"], report["feasibility"])
    render_architecture(report["line_architecture"], report["cost_summary"])
    render_process_chain(report["process_chain"])
    render_warnings(report["feasibility"])
    render_recommendations(report.get("recommendations", []))
    render_trace(report["decision_trace"])
    render_export(report)


# ===================================================================
# COMPONENT LIBRARY PAGE
# ===================================================================

def render_library_page():
    st.subheader(t('library_title'))
    st.caption(t('library_description'))

    try:
        modules_data = load_and_validate_modules()
        modules = modules_data["modules"]
    except Exception as e:
        st.error(f"{t('error_loading_modules')}: {e}")
        return

    categories = sorted(set(m["category"] for m in modules))
    costs = [m["cost_eur"] for m in modules]

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric(t('library_stats_modules'), len(modules))
    with s2:
        st.metric(t('library_stats_categories'), len(categories))
    with s3:
        st.metric(t('library_stats_cost_range'), f"{fmt_compact(min(costs))} - {fmt_compact(max(costs))}")

    st.subheader(t('library_table_title'))

    table_data = []
    for m in modules:
        cat_name = KNOWLEDGE_MODEL.get_module_category_name(m["category"], st.session_state.lang)
        cleanroom_str = t("yes") if m["cleanroom_compatible"] else t("no")
        tolerance_str = f"{m['tolerance_um']} um" if m['tolerance_um'] < 9999 else t("na")
        table_data.append({
            t('lib_col_name'): m["name"],
            t('lib_col_category'): cat_name,
            t('lib_col_cost'): f"{fmt_compact(m['cost_eur'])} EUR",
            t('lib_col_capacity'): f"{m['capacity_ppm']} ppm",
            t('lib_col_footprint'): f"{m['footprint_m2']} m2",
            t('lib_col_energy'): f"{m['energy_kw']} kW",
            t('lib_col_flex'): m["flexibility_score"],
            t('lib_col_cleanroom'): cleanroom_str,
            t('lib_col_tolerance'): tolerance_str,
            t('lib_col_var_flex'): m["variant_flexibility"],
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    st.subheader(t('library_add_title'))
    st.caption(t('library_add_description'))

    with st.form("add_module_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_id = st.text_input(t('field_id'), help=t('field_id_help'))
            new_name = st.text_input(t('field_name'))
            new_category = st.text_input(t('field_category'), help=t('field_category_help'))
            new_cycle = st.number_input(t('field_cycle_time'), min_value=0.0, value=1.0, step=0.1, help=t('field_cycle_time_help'))
            new_capacity = st.number_input(t('field_capacity'), min_value=1.0, value=60.0, step=5.0, help=t('field_capacity_help'))
            new_footprint = st.number_input(t('field_footprint'), min_value=0.1, value=1.0, step=0.1, help=t('field_footprint_help'))
        with c2:
            new_cost = st.number_input(t('field_cost'), min_value=1000, value=25000, step=1000, help=t('field_cost_help'))
            new_energy = st.number_input(t('field_energy'), min_value=0.1, value=1.0, step=0.1, help=t('field_energy_help'))
            new_flex = st.slider(t('field_flexibility'), 1, 10, 5, help=t('field_flexibility_help'))
            new_tolerance = st.number_input(t('field_tolerance'), min_value=1, value=100, step=1, help=t('field_tolerance_help'))
            new_var_flex = st.slider(t('field_variant_flex'), 1, 10, 5, help=t('field_variant_flex_help'))
            new_cleanroom = st.checkbox(t('field_cleanroom'), value=True, help=t('field_cleanroom_help'))

        new_industries = st.text_input(t('field_industries'), help=t('field_industries_help'))
        new_tags = st.text_input(t('field_tags'), help=t('field_tags_help'))

        submitted = st.form_submit_button(t('library_add_button'), type="primary")

    if submitted:
        new_module = {
            "id": new_id.strip(),
            "name": new_name.strip(),
            "category": new_category.strip(),
            "cycle_time_s": new_cycle,
            "capacity_ppm": new_capacity,
            "footprint_m2": new_footprint,
            "cost_eur": new_cost,
            "energy_kw": new_energy,
            "flexibility_score": new_flex,
            "supported_industries": [i.strip() for i in new_industries.split(",") if i.strip()],
            "capability_tags": [tag.strip() for tag in new_tags.split(",") if tag.strip()],
            "cleanroom_compatible": new_cleanroom,
            "tolerance_um": new_tolerance,
            "variant_flexibility": new_var_flex
        }

        existing_ids = {m["id"] for m in modules}
        if new_module["id"] in existing_ids:
            st.error(f"{t('library_add_error')}: {t('library_id_exists')}")
            return

        try:
            _validate_module_item(new_module)
        except Exception as e:
            st.error(f"{t('library_add_error')}: {e}")
            return

        try:
            write_module_to_db(new_module)
            st.success(t('library_added_success'))
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"{t('library_add_error')}: {e}")


# ===================================================================
# MAIN
# ===================================================================

def main():
    render_header()
    selected_product, requirements, generate = render_sidebar()

    page = st.session_state.get("page", "Configurator")

    if page == "Configurator":
        if generate:
            try:
                validate_customer_requirements(requirements)
                modules_data = load_and_validate_modules()
                modules_db = modules_data["modules"]

                with st.spinner(t('status_generating')):
                    report = generate_concept_report(requirements, selected_product, modules_db)

                render_dashboard(report)

            except ValidationError as e:
                st.error(f"{t('error_validation')}: {e}")
            except Exception as e:
                st.error(f"{t('error_engine')}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        else:
            render_welcome()
    else:
        render_library_page()

    # Developer navigation at bottom of main content
    render_footer_nav()


if __name__ == "__main__":
    main()
