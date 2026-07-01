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
from utils.i18n import I18n, set_language, t, get_language
from engine.concept import generate_concept_report, report_to_markdown
from engine.knowledge_model import KNOWLEDGE_MODEL
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
# CSS THEME
# ===================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .studio-header {
        background: #111827;
        color: white;
        padding: 28px 32px;
        border-radius: 10px;
        margin-bottom: 24px;
    }
    .studio-title {
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #ffffff;
        margin: 0;
    }
    .studio-subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-top: 4px;
        font-weight: 400;
    }
    .studio-author {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 8px;
        font-weight: 500;
    }

    .kpi-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 20px 18px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
    }
    .kpi-card.ok::before { background: #059669; }
    .kpi-card.warn::before { background: #d97706; }
    .kpi-card.error::before { background: #dc2626; }
    .kpi-card.neutral::before { background: #2563eb; }
    .kpi-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .kpi-unit {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
        margin-left: 3px;
    }
    .kpi-desc {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 6px;
        line-height: 1.5;
    }

    .arch-banner {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .arch-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
    }
    .arch-reason {
        font-size: 0.88rem;
        color: #4b5563;
        line-height: 1.6;
    }
    .arch-metrics {
        display: flex;
        gap: 24px;
        margin-top: 14px;
        flex-wrap: wrap;
    }
    .arch-metric-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .arch-metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111827;
        margin-top: 2px;
    }

    .pipeline-scroll {
        overflow-x: auto;
        padding: 4px 0 16px 0;
    }
    .pipeline {
        display: flex;
        align-items: stretch;
        gap: 0;
        min-width: max-content;
    }
    .pipe-step {
        min-width: 150px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 14px 12px;
        text-align: center;
        position: relative;
    }
    .pipe-step.ok { border-color: #059669; background: #f0fdf4; }
    .pipe-step.error { border-color: #dc2626; background: #fef2f2; }
    .pipe-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: #2563eb;
        color: white;
        border-radius: 50%;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .pipe-step.ok .pipe-num { background: #059669; }
    .pipe-step.error .pipe-num { background: #dc2626; }
    .pipe-name {
        font-size: 0.65rem;
        font-weight: 700;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 3px;
    }
    .pipe-module {
        font-size: 0.82rem;
        color: #2563eb;
        font-weight: 600;
        line-height: 1.3;
    }
    .pipe-units {
        font-size: 0.72rem;
        color: #6b7280;
        margin-top: 2px;
        font-weight: 500;
    }
    .pipe-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #d1d5db;
        font-size: 1.2rem;
        padding: 0 6px;
        flex-shrink: 0;
        align-self: center;
    }

    .info-box {
        background: #f9fafb;
        border-left: 3px solid #2563eb;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    .info-box.success {
        background: #f0fdf4;
        border-left-color: #059669;
    }
    .info-title {
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
        font-size: 0.95rem;
    }
    .info-text {
        color: #4b5563;
        font-size: 0.87rem;
        line-height: 1.6;
    }

    .warn-box {
        background: #fffbeb;
        border-left: 3px solid #d97706;
        padding: 10px 16px;
        border-radius: 0 6px 6px 0;
        margin: 4px 0;
        color: #92400e;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .error-box {
        background: #fef2f2;
        border-left: 3px solid #dc2626;
        padding: 10px 16px;
        border-radius: 0 6px 6px 0;
        margin: 4px 0;
        color: #991b1b;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .rec-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .rec-card.critical {
        border-color: #dc2626;
        background: #fef2f2;
    }
    .rec-card.advisory {
        border-color: #d97706;
        background: #fffbeb;
    }
    .rec-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #111827;
        margin-bottom: 4px;
    }
    .rec-message {
        color: #4b5563;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 6px;
    }
    .rec-actions {
        color: #6b7280;
        font-size: 0.8rem;
        line-height: 1.5;
    }
    .rec-actions li { margin-bottom: 2px; }

    .trace-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 16px;
        font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
        font-size: 0.75rem;
        color: #374151;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #111827;
        margin: 24px 0 8px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #e5e7eb;
    }
    .section-caption {
        font-size: 0.82rem;
        color: #6b7280;
        margin-bottom: 12px;
        line-height: 1.5;
    }

    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }

    .divider {
        border: none;
        height: 1px;
        background: #e5e7eb;
        margin: 24px 0;
    }

    .progress-bar {
        width: 100%;
        height: 4px;
        background: #e5e7eb;
        border-radius: 2px;
        margin-top: 4px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: #2563eb;
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    .progress-fill.success { background: #059669; }
    .progress-fill.warn { background: #d97706; }
    .progress-fill.danger { background: #dc2626; }

    .css-1oe6wy4 h1 { font-size: 1.0rem !important; color: #111827 !important; font-weight: 700 !important; }
    .css-1oe6wy4 h2 { font-size: 0.88rem !important; color: #374151 !important; font-weight: 600 !important; }

    .step-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 18px;
        text-align: center;
    }
    .step-num {
        font-size: 1.4rem;
        font-weight: 800;
        color: #2563eb;
        margin-bottom: 4px;
    }
    .step-title {
        font-weight: 700;
        color: #111827;
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    .step-text {
        font-size: 0.82rem;
        color: #6b7280;
        line-height: 1.5;
    }

    .lib-stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
    }
    .lib-stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #111827;
    }
    .lib-stat-label {
        font-size: 0.72rem;
        color: #6b7280;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    .compact-display {
        font-size: 0.75rem;
        color: #2563eb;
        font-weight: 600;
        margin-top: -4px;
        margin-bottom: 6px;
        text-align: right;
    }

    .validation-msg {
        font-size: 0.75rem;
        color: #dc2626;
        font-weight: 600;
        margin-top: -4px;
        margin-bottom: 6px;
    }

    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #111827;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        margin-top: 16px;
    }

    .sidebar-divider {
        border: none;
        height: 1px;
        background: #e5e7eb;
        margin: 12px 0;
    }

    .footer-nav {
        border-top: 1px solid #e5e7eb;
        padding-top: 16px;
        margin-top: 40px;
    }
    .footer-nav-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
        text-align: center;
    }

    .kpi-scroll {
        overflow-x: auto;
        padding: 4px 0 16px 0;
    }
    .kpi-row {
        display: flex;
        gap: 12px;
        min-width: max-content;
    }
    .kpi-card-scroll {
        min-width: 180px;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)


# ===================================================================
# HEADER
# ===================================================================

def render_header():
    btn_text = "DE" if st.session_state.lang == "en" else "EN"
    btn_help = t("language_switch")

    col_main, col_btn = st.columns([6, 1])
    with col_main:
        st.markdown(f"""
        <div class="studio-header">
            <div class="studio-title">{t('header_title')}</div>
            <div class="studio-subtitle">{t('header_subtitle')}</div>
            <div class="studio-author">{t('header_author')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
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
    st.sidebar.markdown(f'<p class="sidebar-section-title">{t("section_product")}</p>', unsafe_allow_html=True)

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

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Production Section
    st.sidebar.markdown(f'<p class="sidebar-section-title">{t("section_production")}</p>', unsafe_allow_html=True)

    output_ppm = st.sidebar.number_input(
        t('output_rate_label'), min_value=0.1, value=60.0, step=5.0,
        help=t('output_rate_help'), key="output_ppm"
    )
    st.sidebar.markdown(
        f'<p class="compact-display">{fmt_compact(output_ppm)} {t("kpi_unit_ppm")}</p>',
        unsafe_allow_html=True
    )

    annual_demand = st.sidebar.number_input(
        t('annual_demand_label'), min_value=1, value=500000, step=10000,
        help=t('annual_demand_help'), key="annual_demand"
    )
    st.sidebar.markdown(
        f'<p class="compact-display">{fmt_compact(annual_demand)} {t("kpi_unit_pcs")}</p>',
        unsafe_allow_html=True
    )

    # OEE Slider (50-100) with normalized progress bar
    oee_min, oee_max = 50, 100
    oee_raw = st.sidebar.slider(
        t('oee_label'), oee_min, oee_max, 85, 1,
        help=t('oee_help'), key="oee_slider"
    )
    oee_pct = (oee_raw - oee_min) / (oee_max - oee_min) * 100
    oee_color = "success" if oee_raw >= 80 else "warn" if oee_raw >= 60 else "danger"
    st.sidebar.markdown(f"""
    <div style="margin-top:-8px; margin-bottom:8px;">
        <div class="progress-bar"><div class="progress-fill {oee_color}" style="width:{oee_pct}%"></div></div>
        <p style="font-size:0.72rem; color:#6b7280; margin-top:2px; text-align:right; font-weight:500;">{oee_raw}%</p>
    </div>
    """, unsafe_allow_html=True)

    # Reject Rate Slider (0-20) with normalized progress bar
    rej_min, rej_max = 0, 20
    reject_raw = st.sidebar.slider(
        t('reject_rate_label'), rej_min, rej_max, 2, 1,
        help=t('reject_rate_help'), key="reject_slider"
    )
    rej_pct = (reject_raw - rej_min) / (rej_max - rej_min) * 100
    rej_color = "success" if reject_raw <= 2 else "warn" if reject_raw <= 5 else "danger"
    st.sidebar.markdown(f"""
    <div style="margin-top:-8px; margin-bottom:8px;">
        <div class="progress-bar"><div class="progress-fill {rej_color}" style="width:{rej_pct}%"></div></div>
        <p style="font-size:0.72rem; color:#6b7280; margin-top:2px; text-align:right; font-weight:500;">{reject_raw}%</p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Quality Section
    st.sidebar.markdown(f'<p class="sidebar-section-title">{t("section_quality")}</p>', unsafe_allow_html=True)

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
    st.sidebar.markdown(
        f'<p class="compact-display">{tolerance_um:.1f} um</p>',
        unsafe_allow_html=True
    )

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Constraints Section
    st.sidebar.markdown(f'<p class="sidebar-section-title">{t("section_constraints")}</p>', unsafe_allow_html=True)
    variants = st.sidebar.number_input(
        t('variants_label'), min_value=1, value=1, step=1,
        help=t('variants_help'), key="variants"
    )
    footprint_max = st.sidebar.number_input(
        t('footprint_label'), min_value=0.1, value=50.0, step=1.0,
        help=t('footprint_help'), key="footprint_max"
    )
    st.sidebar.markdown(
        f'<p class="compact-display">{footprint_max:.1f} m2</p>',
        unsafe_allow_html=True
    )
    budget_max = st.sidebar.number_input(
        t('budget_label'), min_value=1000, value=500000, step=10000,
        help=t('budget_help'), key="budget_max"
    )
    st.sidebar.markdown(
        f'<p class="compact-display">{fmt_compact(budget_max)} EUR</p>',
        unsafe_allow_html=True
    )

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
        st.sidebar.markdown(f'<p class="validation-msg">{msg}</p>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # Optimization Section
    st.sidebar.markdown(f'<p class="sidebar-section-title">{t("section_optimization")}</p>', unsafe_allow_html=True)
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
    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f"""
        <div class="info-box">
            <div class="info-title">{t('library_add_title')}</div>
            <div class="info-text">{t('library_add_description')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return None, None, None


# ===================================================================
# FOOTER NAVIGATION (bottom of main content)
# ===================================================================

def render_footer_nav():
    """Developer navigation at the bottom of the main content area."""
    page = st.session_state.get("page", "Configurator")

    st.markdown("<div class='footer-nav'></div>", unsafe_allow_html=True)
    st.markdown(f'<p class="footer-nav-label">{t("page_nav_label")}</p>', unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="info-box">
        <div class="info-title">{t('welcome_title')}</div>
        <div class="info-text">{t('welcome_text')}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-title">{t('step1_title')}</div>
            <div class="step-text">{t('step1_text')}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-title">{t('step2_title')}</div>
            <div class="step-text">{t('step2_text')}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-title">{t('step3_title')}</div>
            <div class="step-text">{t('step3_text')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box success">
        <div class="info-title">{t('how_it_works_title')}</div>
        <div class="info-text">{t('how_it_works_text')}</div>
    </div>
    """, unsafe_allow_html=True)


# ===================================================================
# DASHBOARD
# ===================================================================

def render_kpi_dashboard(kpis, feasibility):
    st.markdown(f"<div class='section-title'>{t('kpi_section_title')}</div>", unsafe_allow_html=True)
    st.caption(t('kpi_section_caption'))

    status = feasibility["status"]
    util = kpis['capacity_utilization'] * 100

    if status == "FAIL":
        util_class = "error"
    elif util < 30 or util > 85:
        util_class = "warn"
    else:
        util_class = "ok"

    # Build each card as a compact inline string (no multi-line f-strings to avoid raw HTML issues)
    c1 = f'<div class="kpi-card kpi-card-scroll {util_class if status == "FAIL" else "neutral"}"><div class="kpi-label">{t("kpi_nominal_rate_title")}</div><div class="kpi-value">{kpis["nominal_rate_ppm"]:.2f}<span class="kpi-unit">{t("kpi_unit_ppm")}</span></div><div class="kpi-desc">{t("kpi_nominal_rate_desc")}</div></div>'
    c2 = f'<div class="kpi-card kpi-card-scroll neutral"><div class="kpi-label">{t("kpi_takt_time_title")}</div><div class="kpi-value">{kpis["takt_time_s"]:.3f}<span class="kpi-unit">{t("kpi_unit_seconds")}</span></div><div class="kpi-desc">{t("kpi_takt_time_desc")}</div></div>'
    c3 = f'<div class="kpi-card kpi-card-scroll neutral"><div class="kpi-label">{t("kpi_annual_capacity_title")}</div><div class="kpi-value">{fmt_compact(kpis["annual_capacity"])}<span class="kpi-unit">{t("kpi_unit_pcs")}</span></div><div class="kpi-desc">{t("kpi_annual_capacity_desc")}</div></div>'
    c4 = f'<div class="kpi-card kpi-card-scroll {util_class}"><div class="kpi-label">{t("kpi_utilization_title")}</div><div class="kpi-value">{util:.1f}<span class="kpi-unit">{t("kpi_unit_percent")}</span></div><div class="kpi-desc">{t("kpi_utilization_desc")}</div></div>'
    c5 = f'<div class="kpi-card kpi-card-scroll {util_class}"><div class="kpi-label">{t("kpi_feasibility_title")}</div><div class="kpi-value">{t(f"status_{status.lower()}")}</div><div class="kpi-desc">{t("kpi_feasibility_desc")}</div></div>'

    # Horizontal scroll container - same pattern as pipeline, compact single-line string
    html = f'<div class="kpi-scroll"><div class="kpi-row">{c1}{c2}{c3}{c4}{c5}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_architecture(line_arch, cost):
    st.markdown(f"<div class='section-title'>{t('arch_section_title')}</div>", unsafe_allow_html=True)

    arch_name = get_architecture_display_name(line_arch.get("type", ""), st.session_state.lang)
    if not arch_name:
        arch_name = line_arch.get('name', '')

    st.markdown(f"""
    <div class="arch-banner">
        <div class="arch-title">{arch_name}</div>
        <div class="arch-reason">{line_arch.get('reason', '')}</div>
        <div class="arch-metrics">
            <div>
                <div class="arch-metric-label">{t('arch_footprint_metric')}</div>
                <div class="arch-metric-value">{cost['total_footprint_m2']:.1f} / {cost['footprint_max_m2']:.0f} m2</div>
            </div>
            <div>
                <div class="arch-metric-label">{t('arch_cost_metric')}</div>
                <div class="arch-metric-value">{fmt_compact(cost['total_cost_eur'])} / {fmt_compact(cost['budget_max_eur'])} EUR</div>
            </div>
            <div>
                <div class="arch-metric-label">{t('arch_energy_metric')}</div>
                <div class="arch-metric-value">{cost['total_energy_kw']:.2f} kW</div>
            </div>
            <div>
                <div class="arch-metric-label">{t('arch_transport_metric')}</div>
                <div class="arch-metric-value">{line_arch.get('recommended_transport', '').replace('_', ' ').title()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_process_chain(process_chain):
    st.markdown(f"<div class='section-title'>{t('process_section_title')}</div>", unsafe_allow_html=True)
    st.caption(t('process_section_caption'))

    pipeline_html = "<div class='pipeline-scroll'><div class='pipeline'>"
    for i, step in enumerate(process_chain):
        mod = step.get("module")
        if mod:
            module_name = mod["name"]
            units = f"x{mod['parallel_units']}"
            css_class = "pipe-step ok"
        else:
            module_name = t('no_module')
            units = ""
            css_class = "pipe-step error"

        op_info = KNOWLEDGE_MODEL.get_operation_info(step["operation_type"], st.session_state.lang)
        op_name = op_info.get("name", step["operation_type"].replace("_", " ").upper()).upper()

        pipeline_html += f"""
        <div class="{css_class}">
            <div class="pipe-num">{step['step']}</div>
            <div class="pipe-name">{op_name}</div>
            <div class="pipe-module">{module_name}</div>
            <div class="pipe-units">{units}</div>
        </div>
        """
        if i < len(process_chain) - 1:
            pipeline_html += '<div class="pipe-arrow">&rarr;</div>'
    pipeline_html += "</div></div>"
    st.markdown(pipeline_html, unsafe_allow_html=True)

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
    st.markdown(f"<div class='section-title'>{t('warnings_title')}</div>", unsafe_allow_html=True)
    for w in feasibility["warnings"]:
        if "overrun" in w.lower() or "exceed" in w.lower() or "budget" in w.lower() or "footprint" in w.lower():
            st.markdown(f'<div class="error-box">{w}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warn-box">{w}</div>', unsafe_allow_html=True)


def render_recommendations(recommendations):
    if not recommendations:
        return
    st.markdown(f"<div class='section-title'>{t('recommendations_title')}</div>", unsafe_allow_html=True)
    st.caption(t('recommendations_caption'))

    for rec in recommendations:
        severity = rec.get("severity", "warning")
        css_class = "critical" if severity == "error" else "advisory"
        title = rec.get(f"title_{st.session_state.lang}", rec.get("title_en", ""))
        message = rec.get(f"message_{st.session_state.lang}", rec.get("message_en", ""))
        actions = rec.get("actions", [])

        actions_html = "<ol style='margin-left:16px;'>"
        for action in actions:
            actions_html += f"<li>{action}</li>"
        actions_html += "</ol>"

        st.markdown(f"""
        <div class="rec-card {css_class}">
            <div class="rec-title">{title} | {t(f'rec_severity_{severity}')}</div>
            <div class="rec-message">{message}</div>
            <div class="rec-actions">{actions_html}</div>
        </div>
        """, unsafe_allow_html=True)


def render_trace(trace):
    st.markdown(f"<div class='section-title'>{t('trace_title')}</div>", unsafe_allow_html=True)
    st.caption(t('trace_caption'))

    trace_html = ""
    for line in trace:
        if line.startswith("KPI:"):
            trace_html += f"<div style='color:#111827; font-weight:700; margin-top:6px; padding-top:4px; border-top:1px solid #e5e7eb;'>[KPI] {line}</div>"
        elif line.startswith("STAGE1"):
            trace_html += f"<div style='color:#2563eb; font-weight:600; margin-top:4px;'>[FILTER] {line}</div>"
        elif line.startswith("STAGE2"):
            trace_html += f"<div style='color:#059669; font-weight:600;'>[CAPACITY] {line}</div>"
        elif line.startswith("STAGE3"):
            trace_html += f"<div style='color:#7c3aed; font-weight:600;'>[SCORE] {line}</div>"
        elif line.startswith("SELECTED"):
            trace_html += f"<div style='color:#059669;'>  OK {line}</div>"
        elif line.startswith("WARNING") or "NO MODULE" in line:
            trace_html += f"<div style='color:#dc2626;'>  ALERT {line}</div>"
        elif line.startswith(("PRODUCT_RULE", "CUSTOMER_RULE", "TRACEABILITY_RULE", "INSPECTION_RULE", "TESTING_RULE", "PACKAGING_RULE", "CLEANROOM_RULE", "GLOBAL_RULE")):
            trace_html += f"<div style='color:#92400e;'>  RULE {line}</div>"
        else:
            trace_html += f"<div>{line}</div>"

    st.markdown(f'<div class="trace-card">{trace_html}</div>', unsafe_allow_html=True)


def render_export(report):
    st.markdown(f"<div class='section-title'>{t('export_title')}</div>", unsafe_allow_html=True)
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
    st.markdown(f"<div class='section-title'>{t('library_title')}</div>", unsafe_allow_html=True)
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
        st.markdown(f"""
        <div class="lib-stat-card">
            <div class="lib-stat-value">{len(modules)}</div>
            <div class="lib-stat-label">{t('library_stats_modules')}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="lib-stat-card">
            <div class="lib-stat-value">{len(categories)}</div>
            <div class="lib-stat-label">{t('library_stats_categories')}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="lib-stat-card">
            <div class="lib-stat-value">{fmt_compact(min(costs))} - {fmt_compact(max(costs))}</div>
            <div class="lib-stat-label">{t('library_stats_cost_range')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>{t('library_table_title')}</div>", unsafe_allow_html=True)

    table_data = []
    for m in modules:
        cat_name = KNOWLEDGE_MODEL.get_module_category_name(m["category"], st.session_state.lang)
        cleanroom_str = t("yes") if m["cleanroom_compatible"] else t("no")
        tolerance_str = f"{m['tolerance_um']} um" if m["tolerance_um"] < 9999 else t("na")
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

    st.markdown(f"<div class='section-title'>{t('library_add_title')}</div>", unsafe_allow_html=True)
    st.caption(t('library_add_description'))

    with st.form("add_module_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_id = st.text_input(t('field_id'), help=t('field_id_help'))
            new_name = st.text_input(t('field_name'))
            # Known categories from Knowledge Model — user selects from dropdown
            known_categories = sorted(KNOWLEDGE_MODEL.MODULE_CATEGORIES.keys())
            new_category = st.selectbox(
                t('field_category'), known_categories,
                help="Select from known module categories. This determines how the module is grouped in the library.",
                key="new_category_select"
            )
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

        # Known capability tags from Knowledge Model — user selects from dropdown
        all_known_tags = sorted(set(
            tag for op in KNOWLEDGE_MODEL.OPERATIONS.values()
            for tag in op.get("capability_tags", [])
        ))
        new_tags = st.multiselect(
            "Capability Tags (select at least one)", all_known_tags,
            help="Select tags that describe what this module can do. The engine uses these tags to match modules to operations. Examples: 'feeding' for part feeders, 'vision' for inspection systems, 'pick_place' for robots.",
            key="new_tags_multiselect"
        )

        new_industries = st.text_input(t('field_industries'), help=t('field_industries_help'))

        submitted = st.form_submit_button(t('library_add_button'), type="primary")

    if submitted:
        if not new_tags:
            st.error("Please select at least one capability tag. Without tags, the module will never be found by the engine.")
            return

        new_module = {
            "id": new_id.strip(),
            "name": new_name.strip(),
            "category": new_category,
            "cycle_time_s": new_cycle,
            "capacity_ppm": new_capacity,
            "footprint_m2": new_footprint,
            "cost_eur": new_cost,
            "energy_kw": new_energy,
            "flexibility_score": new_flex,
            "supported_industries": [i.strip() for i in new_industries.split(",") if i.strip()],
            "capability_tags": new_tags,
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
                    report = generate_concept_report(requirements, selected_product, modules_db, lang=get_language())

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
