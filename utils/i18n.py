class I18n:
    """
    Full internationalization support for Smart Machine Studio.
    Toggle between English and German with session state.
    """

    STRINGS = {
        # Header
        "header_title": {
            "en": "NextGen Smart Machine Studio",
            "de": "NextGen Smart Machine Studio"
        },
        "header_subtitle": {
            "en": "Aalap Janve | Deterministic Engineering Configurator",
            "de": "Aalap Janve | Deterministischer Engineering-Konfigurator"
        },
        "header_author": {
            "en": "Developed by Aalap Janve | Master's Thesis Prototype",
            "de": "Entwickelt von Aalap Janve | Masterarbeit-Prototyp"
        },
        "language_switch": {
            "en": "Switch to German",
            "de": "Switch to English"
        },

        # Sidebar
        "sidebar_title": {
            "en": "Customer Requirements",
            "de": "Kundenanforderungen"
        },
        "sidebar_description": {
            "en": "Define your production needs. The engine translates them into a machine concept.",
            "de": "Definieren Sie Ihre Produktionsanforderungen. Die Engine uebersetzt sie in ein Maschinenkonzept."
        },
        "section_product": {
            "en": "Product Selection",
            "de": "Produktauswahl"
        },
        "product_label": {
            "en": "Product to Manufacture",
            "de": "Zu fertigendes Produkt"
        },
        "product_help": {
            "en": "Select the product type. The engine loads the standard process template for this product.",
            "de": "Waehlen Sie den Produkttyp. Die Engine laedt die Standard-Prozessvorlage fuer dieses Produkt."
        },
        "category_label": {
            "en": "Category",
            "de": "Kategorie"
        },
        "parts_label": {
            "en": "Parts",
            "de": "Teile"
        },

        "section_production": {
            "en": "Production Targets",
            "de": "Produktionsziele"
        },
        "output_rate_label": {
            "en": "Target Output Rate (parts/min)",
            "de": "Ziel-Ausgaberate (Teile/min)"
        },
        "output_rate_help": {
            "en": "How many parts must exit the line every minute?",
            "de": "Wie viele Teile muessen die Linie pro Minute verlassen?"
        },
        "annual_demand_label": {
            "en": "Annual Demand (units)",
            "de": "Jahresbedarf (Einheiten)"
        },
        "annual_demand_help": {
            "en": "Total units needed per year. Used to calculate line utilization.",
            "de": "Gesamteinheiten pro Jahr benoetigt. Wird zur Berechnung der Linienauslastung verwendet."
        },
        "oee_label": {
            "en": "OEE Target (%)",
            "de": "OEE-Ziel (%)"
        },
        "oee_help": {
            "en": "Overall Equipment Effectiveness. Accounts for downtime, speed losses, and quality losses.",
            "de": "Gesamtanlageneffektivitaet. Beruecksichtigt Ausfallzeiten, Geschwindigkeitsverluste und Qualitaetsverluste."
        },
        "reject_rate_label": {
            "en": "Reject Rate (%)",
            "de": "Ausschussrate (%)"
        },
        "reject_rate_help": {
            "en": "Expected percentage of parts that fail quality checks and must be rejected.",
            "de": "Erwarteter Prozentsatz an Teilen, die die Qualitaetspruefung nicht bestehen und ausgeschieden werden muessen."
        },

        "section_quality": {
            "en": "Quality & Environment",
            "de": "Qualitaet & Umgebung"
        },
        "cleanroom_label": {
            "en": "Cleanroom Required",
            "de": "Reinraum erforderlich"
        },
        "cleanroom_help": {
            "en": "Restricts module selection to cleanroom-compatible hardware only.",
            "de": "Schraenkt die Modulauswahl auf reinraum-kompatible Hardware ein."
        },
        "inspection_label": {
            "en": "100% Inspection Required",
            "de": "100%-Inspektion erforderlich"
        },
        "inspection_help": {
            "en": "Adds vision inspection modules. For medical products, this is always enforced.",
            "de": "Fuegt Vision-Inspektionsmodule hinzu. Bei Medizinprodukten wird dies immer erzwungen."
        },
        "traceability_label": {
            "en": "Individual Traceability Required",
            "de": "Individuelle Rueckverfolgbarkeit erforderlich"
        },
        "traceability_help": {
            "en": "Adds laser marking + data logging for part-level tracking (UDI/serials).",
            "de": "Fuegt Laserbeschriftung + Datenprotokollierung fuer Teil-Level-Tracking (UDI/Seriennummern) hinzu."
        },
        "packaging_label": {
            "en": "Packaging Required",
            "de": "Verpackung erforderlich"
        },
        "packaging_help": {
            "en": "Adds end-of-line packaging module (blister, bagging, cartoning).",
            "de": "Fuegt End-of-Line-Verpackungsmodul hinzu (Blister, Beutel, Kartons)."
        },
        "tolerance_label": {
            "en": "Assembly Tolerance (um)",
            "de": "Montagetoleranz (um)"
        },
        "tolerance_help": {
            "en": "Smallest tolerance any module must achieve. Filters out low-precision modules.",
            "de": "Kleinste Toleranz, die jedes Modul erreichen muss. Filtert Module mit niedriger Praezision heraus."
        },

        "section_constraints": {
            "en": "Constraints",
            "de": "Randbedingungen"
        },
        "variants_label": {
            "en": "Product Variants",
            "de": "Produktvarianten"
        },
        "variants_help": {
            "en": "Number of SKUs on the same line. High variants trigger flexible feeders and robot systems.",
            "de": "Anzahl der SKUs auf der gleichen Linie. Hohe Variantenzahlen aktivieren flexible Zufuehrsysteme und Robotersysteme."
        },
        "footprint_label": {
            "en": "Max Floor Space (m2)",
            "de": "Max. Fussabdruck (m2)"
        },
        "footprint_help": {
            "en": "Maximum available production floor area.",
            "de": "Maximal verfuegbare Produktionsflaeche."
        },
        "budget_label": {
            "en": "Budget Limit (EUR)",
            "de": "Budgetlimit (EUR)"
        },
        "budget_help": {
            "en": "Maximum capital expenditure for the line.",
            "de": "Maximale Kapitalkosten fuer die Linie."
        },

        "section_schedule": {
            "en": "Operating Schedule",
            "de": "Betriebsplan"
        },
        "shifts_label": {
            "en": "Shifts per Day",
            "de": "Schichten pro Tag"
        },
        "shifts_help": {
            "en": "Number of production shifts per day (1, 2, or 3).",
            "de": "Anzahl der Produktionsschichten pro Tag (1, 2 oder 3)."
        },
        "hours_label": {
            "en": "Hours per Shift",
            "de": "Stunden pro Schicht"
        },
        "hours_help": {
            "en": "Duration of each production shift in hours.",
            "de": "Dauer jeder Produktionsschicht in Stunden."
        },
        "days_label": {
            "en": "Working Days per Year",
            "de": "Arbeitstage pro Jahr"
        },
        "days_help": {
            "en": "Number of working days per year (1-365).",
            "de": "Anzahl der Arbeitstage pro Jahr (1-365)."
        },

        "section_optimization": {
            "en": "Optimization Priority",
            "de": "Optimierungsprioritaet"
        },
        "optimization_label": {
            "en": "What matters most?",
            "de": "Was ist am wichtigsten?"
        },
        "optimization_help": {
            "en": "The engine scores all valid module combinations and ranks them by this priority.",
            "de": "Die Engine bewertet alle gueltigen Modulkombinationen und ordnet sie nach dieser Prioritaet."
        },
        "opt_cost": {
            "en": "Lowest Total Cost",
            "de": "Niedrigste Gesamtkosten"
        },
        "opt_footprint": {
            "en": "Smallest Floor Space",
            "de": "Kleinster Fussabdruck"
        },
        "opt_energy": {
            "en": "Lowest Energy Consumption",
            "de": "Niedrigster Energieverbrauch"
        },
        "opt_flexibility": {
            "en": "Highest Flexibility",
            "de": "Hoechste Flexibilitaet"
        },

        "generate_button": {
            "en": "GENERATE MACHINE CONCEPT",
            "de": "MASCHINENKONZEPT GENERIEREN"
        },
        "generate_help": {
            "en": "Click to run the deterministic engine. All rules, KPIs, and module selections are fully traceable.",
            "de": "Klicken Sie, um die deterministische Engine zu starten. Alle Regeln, KPIs und Modulauswahlen sind vollstaendig nachvollziehbar."
        },

        # Welcome Page
        "welcome_title": {
            "en": "What does this system do?",
            "de": "Was macht dieses System?"
        },
        "welcome_text": {
            "en": "The NextGen Smart Machine Studio is a deterministic engineering configurator for special-purpose machinery. It translates your customer requirements into a complete, manufacturable machine concept.",
            "de": "Das NextGen Smart Machine Studio ist ein deterministischer Engineering-Konfigurator fuer Sondermaschinen. Es uebersetzt Ihre Kundenanforderungen in ein vollstaendiges, fertigungsgerechtes Maschinenkonzept."
        },
        "step1_title": {
            "en": "1. Input Requirements",
            "de": "1. Anforderungen eingeben"
        },
        "step1_text": {
            "en": "Tell the system what you need to build, how fast, and under what constraints. All inputs are fully validated.",
            "de": "Sagen Sie dem System, was Sie bauen muessen, wie schnell und unter welchen Randbedingungen. Alle Eingaben werden vollstaendig validiert."
        },
        "step2_title": {
            "en": "2. Engine Synthesis",
            "de": "2. Engine-Synthese"
        },
        "step2_text": {
            "en": "The deterministic engine applies ordered engineering rules, computes KPIs, selects modules through a 3-stage pipeline, and validates feasibility. No AI / ML.",
            "de": "Die deterministische Engine wendet geordnete Engineering-Regeln an, berechnet KPIs, waehlt Module durch eine 3-Stufen-Pipeline aus und validiert die Machbarkeit. Keine KI / ML."
        },
        "step3_title": {
            "en": "3. Output Concept",
            "de": "3. Konzept ausgeben"
        },
        "step3_text": {
            "en": "Receive a complete machine concept: process chain, module selections, line architecture, cost summary, and a full decision trace for engineering review.",
            "de": "Erhalten Sie ein vollstaendiges Maschinenkonzept: Prozesskette, Modulauswahl, Linienarchitektur, Kostenuebersicht und einen vollstaendigen Entscheidungspfad zur technischen Ueberpruefung."
        },
        "how_it_works_title": {
            "en": "How the Logic Works",
            "de": "Wie die Logik funktioniert"
        },
        "how_it_works_text": {
            "en": "1) Compute your required production rate from output, OEE, and reject rate. 2) Build the process chain using domain rules. 3) Select the best module for each step using a 3-stage pipeline. 4) Choose the transport architecture. 5) Validate against budget and footprint. Every step is fully traceable.",
            "de": "1) Berechnung der erforderlichen Produktionsrate aus Ausgabe, OEE und Ausschussrate. 2) Erstellung der Prozesskette mit Domain-Regeln. 3) Auswahl des besten Moduls fuer jeden Schritt in einer 3-Stufen-Pipeline. 4) Auswahl der Transportarchitektur. 5) Validierung gegen Budget und Fussabdruck. Jeder Schritt ist vollstaendig nachvollziehbar."
        },

        # KPI Section
        "kpi_section_title": {
            "en": "Production KPIs",
            "de": "Produktions-KPIs"
        },
        "kpi_section_caption": {
            "en": "These values are derived deterministically from your requirements. They are the single source of truth for all downstream decisions.",
            "de": "Diese Werte werden deterministisch aus Ihren Anforderungen abgeleitet. Sie sind die einzige Wahrheitsquelle fuer alle nachgelagerten Entscheidungen."
        },
        "kpi_nominal_rate_title": {
            "en": "Required Nominal Rate",
            "de": "Erforderliche Nennrate"
        },
        "kpi_nominal_rate_desc": {
            "en": "The true production speed the line must achieve, accounting for OEE losses and rejects.",
            "de": "Die tatsaechliche Produktionsgeschwindigkeit, die die Linie erreichen muss, unter Beruecksichtigung von OEE-Verlusten und Ausschuss."
        },
        "kpi_takt_time_title": {
            "en": "Takt Time",
            "de": "Taktzeit"
        },
        "kpi_takt_time_desc": {
            "en": "Time budget per part. Every selected module must complete its cycle within this window.",
            "de": "Zeitbudget pro Teil. Jedes ausgewaehlte Modul muss seinen Zyklus innerhalb dieses Fensters abschliessen."
        },
        "kpi_annual_capacity_title": {
            "en": "Annual Line Capacity",
            "de": "Jaehrliche Linienkapazitaet"
        },
        "kpi_annual_capacity_desc": {
            "en": "Maximum parts the line can produce per year (2-shift, 250 days/year basis).",
            "de": "Maximale Teile, die die Linie pro Jahr produzieren kann (2-Schicht, 250 Tage/Jahr Basis)."
        },
        "kpi_utilization_title": {
            "en": "Capacity Utilization",
            "de": "Kapazitaetsauslastung"
        },
        "kpi_utilization_desc": {
            "en": "Your demand vs. line capacity. Ideal range: 30-85%. Below 30% = over-specified.",
            "de": "Ihr Bedarf vs. Linienkapazitaet. Idealer Bereich: 30-85%. Unter 30% = ueberdimensioniert."
        },
        "kpi_feasibility_title": {
            "en": "Feasibility",
            "de": "Machbarkeit"
        },
        "kpi_feasibility_desc": {
            "en": "Deterministic validation against budget, footprint, and module coverage.",
            "de": "Deterministische Validierung gegen Budget, Fussabdruck und Modulabdeckung."
        },
        "kpi_unit_ppm": {
            "en": "ppm",
            "de": "Teile/min"
        },
        "kpi_unit_seconds": {
            "en": "s",
            "de": "s"
        },
        "kpi_unit_pcs": {
            "en": "pcs",
            "de": "Stk"
        },
        "kpi_unit_percent": {
            "en": "%",
            "de": "%"
        },

        # Architecture
        "arch_section_title": {
            "en": "Recommended Line Architecture",
            "de": "Empfohlene Linienarchitektur"
        },
        "arch_footprint_metric": {
            "en": "Total Footprint",
            "de": "Gesamtflaeche"
        },
        "arch_cost_metric": {
            "en": "Total Cost",
            "de": "Gesamtkosten"
        },
        "arch_energy_metric": {
            "en": "Total Energy",
            "de": "Gesamtenergie"
        },
        "arch_transport_metric": {
            "en": "Transport System",
            "de": "Transportsystem"
        },

        # Process Chain
        "process_section_title": {
            "en": "Process Chain",
            "de": "Prozesskette"
        },
        "process_section_caption": {
            "en": "Each block represents a process step. The module inside is the best-ranked selection from the 3-stage pipeline.",
            "de": "Jeder Block repraesentiert einen Prozessschritt. Das Modul darin ist die am besten bewertete Auswahl aus der 3-Stufen-Pipeline."
        },
        "process_table_title": {
            "en": "Detailed Module Selection",
            "de": "Detaillierte Modulauswahl"
        },
        "col_step": {"en": "Step", "de": "Schritt"},
        "col_operation": {"en": "Operation", "de": "Operation"},
        "col_module": {"en": "Selected Module", "de": "Ausgewaehltes Modul"},
        "col_units": {"en": "Parallel Units", "de": "Parallele Einheiten"},
        "col_unit_cost": {"en": "Unit Cost", "de": "Stueckkosten"},
        "col_total_cost": {"en": "Total Cost", "de": "Gesamtkosten"},
        "col_footprint": {"en": "Total Footprint", "de": "Gesamtflaeche"},
        "col_score": {"en": "Engine Score", "de": "Engine-Bewertung"},
        "no_module": {"en": "NO COMPATIBLE MODULE", "de": "KEIN KOMPATIBLES MODUL"},

        # Warnings
        "warnings_title": {
            "en": "Engineering Warnings",
            "de": "Technische Warnungen"
        },

        # Decision Trace
        "trace_title": {
            "en": "Decision Trace",
            "de": "Entscheidungspfad"
        },
        "trace_caption": {
            "en": "Every rule hit, every filter stage, and every module selection is logged below. This is the explainability layer of the engine.",
            "de": "Jeder Regeltreffer, jede Filterstufe und jede Modulauswahl wird unten protokolliert. Dies ist die Erklaerbarkeits-Schicht der Engine."
        },

        # Export
        "export_title": {
            "en": "Export Concept Report",
            "de": "Konzeptbericht exportieren"
        },
        "export_json": {
            "en": "Download JSON",
            "de": "JSON herunterladen"
        },
        "export_md": {
            "en": "Download Markdown",
            "de": "Markdown herunterladen"
        },
        "export_json_caption": {
            "en": "Use the JSON file for downstream CAD/ERP integration.",
            "de": "Verwenden Sie die JSON-Datei fuer die nachgelagerte CAD/ERP-Integration."
        },
        "history_title": {"en": "Concept History", "de": "Konzept-Verlauf"},
        "history_description": {
            "en": "Previously generated concepts. Click to reload a concept.",
            "de": "Zuvor generierte Konzepte. Klicken Sie, um ein Konzept neu zu laden."
        },
        "history_empty": {"en": "No concepts generated yet.", "de": "Noch keine Konzepte generiert."},
        "history_load": {"en": "Load", "de": "Laden"},
        "history_clear": {"en": "Clear History", "de": "Verlauf loeschen"},

        # Status Messages
        "status_pass": {"en": "PASS", "de": "BESTANDEN"},
        "status_fail": {"en": "FAIL", "de": "FEHLGESCHLAGEN"},
        "status_generating": {
            "en": "Running deterministic engine...",
            "de": "Deterministische Engine laeuft..."
        },
        "error_validation": {
            "en": "Validation Error",
            "de": "Validierungsfehler"
        },
        "error_engine": {
            "en": "Engine Error",
            "de": "Engine-Fehler"
        },
        "welcome_prompt": {
            "en": "Configure requirements in the sidebar and click GENERATE MACHINE CONCEPT to synthesize the machine concept.",
            "de": "Konfigurieren Sie die Anforderungen in der Seitenleiste und klicken Sie auf MASCHINENKONZEPT GENERIEREN, um das Maschinenkonzept zu synthetisieren."
        },
        "spinner_text": {
            "en": "Running deterministic engine...",
            "de": "Deterministische Engine laeuft..."
        },

        # Report Labels
        "report_product": {"en": "Product", "de": "Produkt"},
        "report_category": {"en": "Category", "de": "Kategorie"},
        "report_kpis": {"en": "KPIs - Production Metrics", "de": "KPIs - Produktionskennzahlen"},
        "report_architecture": {"en": "Line Architecture", "de": "Linienarchitektur"},
        "report_process_chain": {"en": "Process Chain", "de": "Prozesskette"},
        "report_cost_summary": {"en": "Cost Summary", "de": "Kostenuebersicht"},
        "report_feasibility": {"en": "Feasibility", "de": "Machbarkeit"},
        "report_trace": {"en": "Decision Trace", "de": "Entscheidungspfad"},
        "report_warnings": {"en": "Warnings", "de": "Warnungen"},
        "report_none": {"en": "None", "de": "Keine"},
        "recommendations_title": {"en": "Engineering Recommendations", "de": "Engineering-Empfehlungen"},
        "recommendations_caption": {"en": "Based on the Knowledge Model analysis, the following actions are recommended:", "de": "Basierend auf der Knowledge-Model-Analyse werden folgende Massnahmen empfohlen:"},
        "rec_action": {"en": "Recommended Action", "de": "Empfohlene Massnahme"},
        "rec_severity_error": {"en": "Critical", "de": "Kritisch"},
        "rec_severity_warning": {"en": "Advisory", "de": "Empfohlen"},

        # Page Switcher
        "page_configurator": {"en": "Configurator", "de": "Konfigurator"},
        "page_library": {"en": "Component Library", "de": "Komponentenbibliothek"},

        # Library Page
        "library_title": {"en": "Component Library", "de": "Komponentenbibliothek"},
        "library_description": {
            "en": "All modules available in the system. Each module has been validated for engineering parameters.",
            "de": "Alle im System verfuegbaren Module. Jedes Modul wurde auf Engineering-Parameter validiert."
        },
        "library_table_title": {"en": "All Modules", "de": "Alle Module"},
        "library_stats_modules": {"en": "Total Modules", "de": "Gesamtmodule"},
        "library_stats_categories": {"en": "Categories", "de": "Kategorien"},
        "library_stats_cost_range": {"en": "Cost Range", "de": "Kostenbereich"},
        "library_add_title": {"en": "Add New Module", "de": "Neues Modul hinzufuegen"},
        "library_add_description": {
            "en": "Fill in all fields to add a new module to the database. All fields are validated before saving.",
            "de": "Fuellen Sie alle Felder aus, um ein neues Modul zur Datenbank hinzuzufuegen. Alle Felder werden vor dem Speichern validiert."
        },
        "library_add_button": {"en": "Add Module to Database", "de": "Modul zur Datenbank hinzufuegen"},
        "library_added_success": {"en": "Module added successfully. Reloading...", "de": "Modul erfolgreich hinzugefuegt. Wird neu geladen..."},
        "library_add_error": {"en": "Validation error", "de": "Validierungsfehler"},
        "library_id_exists": {"en": "A module with this ID already exists.", "de": "Ein Modul mit dieser ID existiert bereits."},
        "library_delete_button": {"en": "Delete", "de": "Loeschen"},
        "library_deleted_success": {"en": "Module deleted successfully. Reloading...", "de": "Modul erfolgreich geloescht. Wird neu geladen..."},
        "library_delete_confirm": {"en": "Are you sure you want to delete this module?", "de": "Sind Sie sicher, dass Sie dieses Modul loeschen moechten?"},

        # Reset button
        "reset_button": {"en": "Reset to Defaults", "de": "Zuruecksetzen auf Standardwerte"},
        "reset_help": {"en": "Reset all inputs to their default values", "de": "Alle Eingaben auf Standardwerte zuruecksetzen"},

        # Developer page
        "page_developer": {"en": "Developer Tools", "de": "Entwickler-Tools"},
        "dev_tools_title": {"en": "Developer Tools", "de": "Entwickler-Tools"},
        "dev_tools_description": {"en": "Concept management and system validation tools.", "de": "Konzeptverwaltungs- und Systemvalidierungstools."},
        "dev_history_title": {"en": "Concept History", "de": "Konzept-Verlauf"},
        "dev_history_description": {"en": "Previously generated concepts. Click Load to view, or Compare to see side-by-side.", "de": "Zuvor generierte Konzepte. Klicken Sie auf Laden zum Anzeigen oder Vergleichen fuer eine Seite-an-Seite-Ansicht."},
        "dev_compare_title": {"en": "Compare Concepts", "de": "Konzepte vergleichen"},
        "dev_compare_description": {"en": "Select two concepts to compare side-by-side.", "de": "Waehlen Sie zwei Konzepte zum Seite-an-Seite-Vergleichen aus."},
        "dev_compare_select_1": {"en": "Select Concept A", "de": "Konzept A auswaehlen"},
        "dev_compare_select_2": {"en": "Select Concept B", "de": "Konzept B auswaehlen"},
        "dev_test_tools_title": {"en": "Quick Test", "de": "Schnelltest"},
        "dev_test_tools_description": {"en": "Generate a concept with random requirements to test engine stability.", "de": "Generieren Sie ein Konzept mit zufaelligen Anforderungen, um die Engine-Stabilitaet zu testen."},
        "dev_quick_test_button": {"en": "Run Random Test", "de": "Zufaelligen Test ausfuehren"},
        "dev_quick_test_help": {"en": "Generates a concept with random but valid inputs.", "de": "Generiert ein Konzept mit zufaelligen, aber gueltigen Eingaben."},
        "dev_test_pass": {"en": "Test passed — engine generated a valid concept.", "de": "Test bestanden — Engine hat ein gueltiges Konzept generiert."},
        "dev_test_fail": {"en": "Test failed — {error}", "de": "Test fehlgeschlagen — {error}"},
        "dev_module_stats": {"en": "Module Database Stats", "de": "Modul-Datenbank-Statistiken"},
        "dev_total_modules": {"en": "Total Modules", "de": "Gesamtmodule"},
        "dev_total_products": {"en": "Total Products", "de": "Gesamtprodukte"},
        "dev_back": {"en": "Back to Configurator", "de": "Zurueck zum Konfigurator"},
        "dev_no_history": {"en": "No concepts in history. Generate some concepts first.", "de": "Keine Konzepte im Verlauf. Generieren Sie zuerst einige Konzepte."},
        "dev_load": {"en": "Load", "de": "Laden"},
        "dev_compare": {"en": "Compare", "de": "Vergleichen"},
        "dev_remove": {"en": "Remove", "de": "Entfernen"},

        # Form field labels
        "field_id": {"en": "Module ID", "de": "Modul-ID"},
        "field_name": {"en": "Module Name", "de": "Modulname"},
        "field_category": {"en": "Category", "de": "Kategorie"},
        "field_cycle_time": {"en": "Cycle Time (s)", "de": "Zykluszeit (s)"},
        "field_capacity": {"en": "Capacity (ppm)", "de": "Kapazitaet (Teile/min)"},
        "field_footprint": {"en": "Footprint (m2)", "de": "Fussabdruck (m2)"},
        "field_cost": {"en": "Cost (EUR)", "de": "Kosten (EUR)"},
        "field_energy": {"en": "Energy (kW)", "de": "Energie (kW)"},
        "field_flexibility": {"en": "Flexibility Score (1-10)", "de": "Flexibilitaetswert (1-10)"},
        "field_tolerance": {"en": "Tolerance (um)", "de": "Toleranz (um)"},
        "field_variant_flex": {"en": "Variant Flexibility (1-10)", "de": "Variantenflexibilitaet (1-10)"},
        "field_cleanroom": {"en": "Cleanroom Compatible", "de": "Reinraum-kompatibel"},
        "field_industries": {"en": "Supported Industries (comma-separated)", "de": "Unterstuetzte Industrien (kommagetrennt)"},
        "field_tags": {"en": "Capability Tags (comma-separated)", "de": "Faehigkeits-Tags (kommagetrennt)"},
        "field_id_help": {"en": "Unique identifier, e.g., mod_custom_01", "de": "Eindeutige Kennung, z.B. mod_custom_01"},
        "field_category_help": {"en": "e.g., feeding_systems, robot_cells, inspection_systems", "de": "z.B. zufuehrsysteme, roboterzellen, inspektionssysteme"},
        "field_industries_help": {"en": "e.g., medical, consumer_goods, industrial_components", "de": "z.B. medical, consumer_goods, industrial_components"},
        "field_tags_help": {"en": "e.g., feeding, orienting, vision", "de": "z.B. feeding, orienting, vision"},

        # Library table columns
        "lib_col_name": {"en": "Name", "de": "Name"},
        "lib_col_category": {"en": "Category", "de": "Kategorie"},
        "lib_col_cost": {"en": "Cost", "de": "Kosten"},
        "lib_col_capacity": {"en": "Capacity", "de": "Kapazitaet"},
        "lib_col_footprint": {"en": "Footprint", "de": "Fussabdruck"},
        "lib_col_energy": {"en": "Energy", "de": "Energie"},
        "lib_col_flex": {"en": "Flex", "de": "Flex"},
        "lib_col_cleanroom": {"en": "Cleanroom", "de": "Reinraum"},
        "lib_col_tolerance": {"en": "Tolerance", "de": "Toleranz"},
        "lib_col_var_flex": {"en": "Var. Flex", "de": "Var. Flex"},

        # Missing translations
        "yes": {"en": "Yes", "de": "Ja"},
        "no": {"en": "No", "de": "Nein"},
        "na": {"en": "N/A", "de": "N/A"},
        "error_loading_modules": {"en": "Error loading modules", "de": "Fehler beim Laden der Module"},
        "page_nav_label": {"en": "Developer Navigation", "de": "Entwickler-Navigation"},
        "budget_compact_display": {"en": "Budget: {value} EUR", "de": "Budget: {value} EUR"},
        "transport_system_label": {"en": "Transport System", "de": "Transportsystem"},

        # Validation errors
        "err_output_ppm_positive": {"en": "Output rate must be greater than 0", "de": "Ausgaberate muss groesser als 0 sein"},
        "err_annual_demand_positive": {"en": "Annual demand must be greater than 0", "de": "Jahresbedarf muss groesser als 0 sein"},
        "err_oee_range": {"en": "OEE must be between 50% and 100%", "de": "OEE muss zwischen 50% und 100% liegen"},
        "err_reject_range": {"en": "Reject rate must be between 0% and 100%", "de": "Ausschussrate muss zwischen 0% und 100% liegen"},
        "err_tolerance_positive": {"en": "Tolerance must be greater than 0", "de": "Toleranz muss groesser als 0 sein"},
        "err_variants_positive": {"en": "Variants must be at least 1", "de": "Varianten muessen mindestens 1 sein"},
        "err_footprint_positive": {"en": "Footprint must be greater than 0", "de": "Fussabdruck muss groesser als 0 sein"},
        "err_budget_positive": {"en": "Budget must be greater than 0", "de": "Budget muss groesser als 0 sein"},

        # Form field help texts
        "field_cycle_time_help": {"en": "Time for one complete cycle of the module in seconds", "de": "Zeit fuer einen kompletten Zyklus des Moduls in Sekunden"},
        "field_capacity_help": {"en": "Maximum parts per minute the module can process", "de": "Maximale Teile pro Minute, die das Modul verarbeiten kann"},
        "field_footprint_help": {"en": "Floor space required by one module unit in square meters", "de": "Benoetigte Bodenflaeche eines Modul-Einheit in Quadratmetern"},
        "field_cost_help": {"en": "Cost of one module unit in EUR", "de": "Kosten einer Modul-Einheit in EUR"},
        "field_energy_help": {"en": "Energy consumption of one module unit in kW", "de": "Energieverbrauch einer Modul-Einheit in kW"},
        "field_flexibility_help": {"en": "How easily the module adapts to different products (1 = rigid, 10 = very flexible)", "de": "Wie leicht das Modul sich an verschiedene Produkte anpasst (1 = starr, 10 = sehr flexibel)"},
        "field_tolerance_help": {"en": "Smallest achievable tolerance in micrometers. Use 9999 for no constraint.", "de": "Kleinste erreichbare Toleranz in Mikrometern. 9999 fuer keine Beschraenkung."},
        "field_variant_flex_help": {"en": "How many product variants the module can handle (1 = single variant, 10 = high variety)", "de": "Wie viele Produktvarianten das Modul handhaben kann (1 = Einzelvariante, 10 = hohe Vielfalt)"},
        "field_cleanroom_help": {"en": "Whether the module is compatible with cleanroom environments (ISO 14644-1)", "de": "Ob das Modul mit Reinraum-Umgebungen kompatibel ist (ISO 14644-1)"},
    }

    def __init__(self, lang: str = "en"):
        self._lang = lang

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str):
        if value not in ("en", "de"):
            raise ValueError("Language must be 'en' or 'de'")
        self._lang = value

    def get(self, key: str) -> str:
        """Get translated string for current language."""
        entry = self.STRINGS.get(key, {})
        return entry.get(self._lang, entry.get("en", key))

    def __call__(self, key: str) -> str:
        """Convenience: i18n('key') returns translated string."""
        val = self.get(key)
        if val == key:
            import logging
            logging.getLogger("smart_machine_studio.i18n").warning(f"Missing i18n key: {key}")
        return val


# Global instance - UI sets language via session_state
_i18n = I18n("en")

def set_language(lang: str):
    """Set global language."""
    _i18n.lang = lang

def get_i18n() -> I18n:
    """Get current i18n instance."""
    return _i18n

def get_language() -> str:
    """Get current global language."""
    return _i18n.lang

def t(key: str) -> str:
    """Shorthand translation function."""
    return _i18n(key)
