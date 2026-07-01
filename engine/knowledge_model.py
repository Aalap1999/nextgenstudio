from typing import Dict, Any, List, Set, Tuple, Optional
from math import ceil

class KnowledgeModel:
    """
    Central Engineering Knowledge Model for the Smart Machine Studio.

    Encodes the expertise of a senior automation engineer in a deterministic,
    queryable form. This is the 'brain' that replaces manual conceptual design.

    Contains:
      - Product taxonomy and domain knowledge
      - Operation ontology with capability mapping
      - Transfer functions (input-output relationships)
      - Ordered domain rules
      - Architecture selection rules
      - Recommendation engine for warnings and optimization
      - Bottleneck analysis rules
      - Line balancing knowledge
    """

    # ═══════════════════════════════════════════════════════════════════
    # 1. PRODUCT TAXONOMY
    # ═══════════════════════════════════════════════════════════════════
    PRODUCT_CATEGORIES = {
        "medical": {
            "description_en": "Medical device manufacturing (e.g., lancets, syringes, catheters)",
            "description_de": "Medizinprodukte-Fertigung (z.B. Lanzetten, Spritzen, Katheter)",
            "default_cleanroom": True,
            "inspection_enforced": True,
            "traceability_common": True,
            "typical_tolerance_um": 50,
            "preferred_feeder": "tray_feeder",
            "preferred_transport": "pallet_conveyor",
            "notes_en": "Medical devices require ISO 14644-1 compliant cleanrooms, 100% inspection, and individual traceability (UDI).",
            "notes_de": "Medizinprodukte erfordern ISO-14644-1-konforme Reinräume, 100%-Inspektion und individuelle Rückverfolgbarkeit (UDI).",
        },
        "consumer_goods": {
            "description_en": "Consumer product assembly (e.g., razors, cosmetics, small appliances)",
            "description_de": "Konsumgüter-Montage (z.B. Rasierer, Kosmetik, Kleingeräte)",
            "default_cleanroom": False,
            "inspection_enforced": False,
            "traceability_common": False,
            "typical_tolerance_um": 100,
            "preferred_feeder": "bowl_feeder",
            "preferred_transport": "pallet_conveyor",
            "notes_en": "Consumer goods prioritize cost and throughput. Vision inspection is optional unless high quality standards are specified.",
            "notes_de": "Konsumgüter priorisieren Kosten und Durchsatz. Vision-Inspektion ist optional, es sei denn, hohe Qualitätsstandards sind vorgegeben.",
        },
        "industrial_components": {
            "description_en": "Industrial component assembly (e.g., connectors, sensors, housings)",
            "description_de": "Industriekomponenten-Montage (z.B. Stecker, Sensoren, Gehäuse)",
            "default_cleanroom": False,
            "inspection_enforced": False,
            "traceability_common": False,
            "typical_tolerance_um": 100,
            "preferred_feeder": "bowl_feeder",
            "preferred_transport": "linear_transport",
            "notes_en": "Industrial components often require electrical testing and tight tolerances. High throughput is common.",
            "description_de": "Industriekomponenten erfordern oft elektrische Prüfung und enge Toleranzen. Hoher Durchsatz ist üblich.",
        }
    }

    # ═══════════════════════════════════════════════════════════════════
    # 2. OPERATION ONTOLOGY
    # ═══════════════════════════════════════════════════════════════════
    OPERATIONS = {
        "feeding": {
            "en": "Part Feeding & Orienting",
            "de": "Teile-Zufuehrung & Ausrichtung",
            "capability_tags": ["feeding", "orienting", "bulk_supply", "precision_orienting", "tray_supply", "vision_orienting", "multi_variant", "linear", "simple_orienting"],
            "description_en": "Supply and orient individual parts from bulk, trays, or magazines.",
            "description_de": "Zufuehrung und Ausrichtung einzelner Teile aus Schuettgut, Trays oder Magazinen.",
            "typical_cycle_s": 0.5,
            "is_bottleneck_prone": False,
        },
        "assembly": {
            "en": "Assembly / Pick & Place",
            "de": "Montage / Pick & Place",
            "capability_tags": ["assembly", "pick_place", "fast_cycle", "complex_motion"],
            "description_en": "Join parts together using robotic or mechanical assembly.",
            "description_de": "Zusammenfuegen von Teilen durch robotergestuetzte oder mechanische Montage.",
            "typical_cycle_s": 0.6,
            "is_bottleneck_prone": True,
        },
        "insertion": {
            "en": "Insertion / Pressing",
            "de": "Einfuegen / Pressen",
            "capability_tags": ["insertion", "pressing", "force_control", "clip", "snap_fit"],
            "description_en": "Insert components into housings or apply controlled force.",
            "description_de": "Einfuegen von Komponenten in Gehaeuse oder Aufbringen kontrollierter Kraefte.",
            "typical_cycle_s": 0.8,
            "is_bottleneck_prone": True,
        },
        "testing": {
            "en": "Functional Testing",
            "de": "Funktionspruefung",
            "capability_tags": ["testing", "force", "spring", "mechanical", "leak", "pressure", "seal", "electrical", "continuity", "isolation"],
            "description_en": "Verify part function: force-displacement, leak, electrical, etc.",
            "description_de": "Funktionspruefung: Kraft-Weg, Dichtheit, elektrisch, usw.",
            "typical_cycle_s": 1.5,
            "is_bottleneck_prone": True,
        },
        "inspection": {
            "en": "Vision Inspection",
            "de": "Vision-Inspektion",
            "capability_tags": ["inspection", "vision", "2d", "3d", "surface_check", "dimension_check"],
            "description_en": "Optical quality control using 2D or 3D vision systems.",
            "description_de": "Optische Qualitaetskontrolle mit 2D- oder 3D-Vision-Systemen.",
            "typical_cycle_s": 0.5,
            "is_bottleneck_prone": False,
        },
        "marking": {
            "en": "Marking / Traceability",
            "de": "Beschriftung / Rueckverfolgbarkeit",
            "capability_tags": ["marking", "laser", "traceability", "code"],
            "description_en": "Apply serial numbers, codes, or UDI for traceability.",
            "description_de": "Aufbringen von Seriennummern, Codes oder UDI fuer Rueckverfolgbarkeit.",
            "typical_cycle_s": 0.8,
            "is_bottleneck_prone": False,
        },
        "packaging": {
            "en": "Packaging",
            "de": "Verpackung",
            "capability_tags": ["packaging", "bagging", "blister", "cartoning", "stacking", "palletizing"],
            "description_en": "End-of-line packaging into bags, blisters, cartons, or trays.",
            "description_de": "End-of-Line-Verpackung in Beutel, Blister, Kartons oder Trays.",
            "typical_cycle_s": 1.2,
            "is_bottleneck_prone": False,
        },
        "control": {
            "en": "PLC Control Cabinet",
            "de": "SPS-Schaltschrank",
            "capability_tags": ["control", "plc", "safety", "logic"],
            "description_en": "Central safety and control logic for the entire line.",
            "description_de": "Zentrale Sicherheits- und Steuerungslogik fuer die gesamte Linie.",
            "typical_cycle_s": 0.0,
            "is_bottleneck_prone": False,
        },
        "hmi": {
            "en": "HMI Operator Station",
            "de": "HMI-Bedienstation",
            "capability_tags": ["hmi", "operator", "visualization"],
            "description_en": "Human-Machine Interface for operators and maintenance.",
            "description_de": "Mensch-Maschine-Schnittstelle fuer Bediener und Wartung.",
            "typical_cycle_s": 0.0,
            "is_bottleneck_prone": False,
        },
        "data_logging": {
            "en": "Data Logging / MES Interface",
            "de": "Datenprotokollierung / MES-Schnittstelle",
            "capability_tags": ["data", "database", "mes"],
            "description_en": "Traceability database and MES integration.",
            "description_de": "Rueckverfolgbarkeitsdatenbank und MES-Anbindung.",
            "typical_cycle_s": 0.0,
            "is_bottleneck_prone": False,
        },
        "reject": {
            "en": "Reject Handling",
            "de": "Ausschuss-Handling",
            "capability_tags": ["reject", "sorting", "ng_handling"],
            "description_en": "Separate and handle defective parts.",
            "description_de": "Trennen und Handhaben von defekten Teilen.",
            "typical_cycle_s": 0.5,
            "is_bottleneck_prone": False,
        }
    }

    # ═══════════════════════════════════════════════════════════════════
    # 3. TRANSFER FUNCTIONS (Engineering Relationships)
    # ═══════════════════════════════════════════════════════════════════
    # These are the mathematical relationships that transform customer
    # requirements into machine parameters. In control theory, a transfer
    # function G(s) = Output(s) / Input(s). Here we encode the same
    # deterministic relationships for special-purpose machinery design.

    TRANSFER_FUNCTIONS = {
        "nominal_rate": {
            "symbol": "R_nom",
            "en": "Nominal Rate = Output / (OEE * (1 - Reject Rate))",
            "de": "Nennrate = Ausgabe / (OEE * (1 - Ausschussrate))",
            "description_en": "Transfer function: converts target output to required nominal production rate, accounting for availability and quality losses.",
            "description_de": "Transferfunktion: Wandelt Ziel-Ausgabe in erforderliche Nennproduktionsrate um, unter Beruecksichtigung von Verfuegbarkeits- und Qualitaetsverlusten.",
            "inputs": ["output_ppm", "oee_target", "reject_rate"],
            "output": "nominal_rate_ppm",
            "formula": lambda output, oee, reject: output / (oee * (1 - reject)),
        },
        "takt_time": {
            "symbol": "T_takt",
            "en": "Takt Time = 60 / Nominal Rate",
            "de": "Taktzeit = 60 / Nennrate",
            "description_en": "Transfer function: converts nominal rate to the time budget available per part.",
            "description_de": "Transferfunktion: Wandelt Nennrate in das Zeitbudget pro Teil um.",
            "inputs": ["nominal_rate_ppm"],
            "output": "takt_time_s",
            "formula": lambda nominal_rate: 60.0 / nominal_rate,
        },
        "parallel_units": {
            "symbol": "N_par",
            "en": "Parallel Units = ceil(Nominal Rate / Module Capacity)",
            "de": "Parallele Einheiten = ceil(Nennrate / Modulkapazitaet)",
            "description_en": "Transfer function: determines how many identical modules must run in parallel to meet the takt time.",
            "description_de": "Transferfunktion: Bestimmt, wie viele identische Module parallel laufen muessen, um die Taktzeit zu erreichen.",
            "inputs": ["nominal_rate_ppm", "module_capacity_ppm"],
            "output": "parallel_units",
            "formula": lambda nominal_rate, module_capacity: ceil(nominal_rate / module_capacity),
        },
        "annual_capacity": {
            "symbol": "C_annual",
            "en": "Annual Capacity = Nominal Rate * 60 * 16 * 250",
            "de": "Jahreskapazitaet = Nennrate * 60 * 16 * 250",
            "description_en": "Transfer function: converts nominal rate to annual production capacity (2-shift, 250 days/year).",
            "description_de": "Transferfunktion: Wandelt Nennrate in Jahresproduktionskapazitaet um (2-Schicht, 250 Tage/Jahr).",
            "inputs": ["nominal_rate_ppm"],
            "output": "annual_capacity",
            "formula": lambda nominal_rate: nominal_rate * 60 * 16 * 250,
        },
        "capacity_utilization": {
            "symbol": "U_cap",
            "en": "Capacity Utilization = Annual Demand / Annual Capacity",
            "de": "Kapazitaetsauslastung = Jahresbedarf / Jahreskapazitaet",
            "description_en": "Transfer function: measures how much of the line capacity is consumed by demand.",
            "description_de": "Transferfunktion: Misst, wie viel der Linienkapazitaet vom Bedarf verbraucht wird.",
            "inputs": ["annual_demand", "annual_capacity"],
            "output": "capacity_utilization",
            "formula": lambda demand, capacity: demand / capacity if capacity > 0 else 0.0,
        },
        "total_cost": {
            "symbol": "C_total",
            "en": "Total Cost = sum(Parallel Units * Unit Cost) for all modules",
            "de": "Gesamtkosten = Summe(Parallele Einheiten * Stueckkosten) fuer alle Module",
            "description_en": "Transfer function: aggregates module costs including parallelization.",
            "description_de": "Transferfunktion: Aggregiert Modulkosten einschliesslich Parallelisierung.",
            "inputs": ["module_parallel_units", "module_unit_cost"],
            "output": "total_cost_eur",
            "formula": lambda units, costs: sum(u * c for u, c in zip(units, costs)),
        },
        "total_footprint": {
            "symbol": "A_total",
            "en": "Total Footprint = sum(Parallel Units * Unit Footprint) for all modules",
            "de": "Gesamtflaeche = Summe(Parallele Einheiten * Stueckflaeche) fuer alle Module",
            "description_en": "Transfer function: aggregates module footprints including parallelization.",
            "description_de": "Transferfunktion: Aggregiert Modulflaechen einschliesslich Parallelisierung.",
            "inputs": ["module_parallel_units", "module_unit_footprint"],
            "output": "total_footprint_m2",
            "formula": lambda units, footprints: sum(u * f for u, f in zip(units, footprints)),
        },
    }

    # ═══════════════════════════════════════════════════════════════════
    # 4. DOMAIN RULES (Ordered, Deterministic)
    # ═══════════════════════════════════════════════════════════════════
    DOMAIN_RULES = [
        {
            "id": "product_cleanroom",
            "name_en": "Product Cleanroom Enforcement",
            "name_de": "Produkt-Reinraum-Zwang",
            "trigger": "product.default_cleanroom_requirement and not requirements.cleanroom_required",
            "action": "set requirements.cleanroom_required = True",
            "description_en": "Certain products (e.g., medical) always require cleanroom regardless of checkbox.",
            "description_de": "Bestimmte Produkte (z.B. Medizin) erfordern immer Reinraum, unabhaengig von Checkbox.",
            "priority": 1,
        },
        {
            "id": "customer_inspection",
            "name_en": "Customer Inspection Requirement",
            "name_de": "Kunden-Inspektionsanforderung",
            "trigger": "requirements.inspection_required",
            "action": "add_or_enforce inspection operation",
            "description_en": "If customer requires inspection, add vision inspection module to the chain.",
            "description_de": "Wenn Kunde Inspektion verlangt, Vision-Inspektionsmodul zur Kette hinzufuegen.",
            "priority": 2,
        },
        {
            "id": "traceability_marking",
            "name_en": "Traceability Marking & Data Logging",
            "name_de": "Rueckverfolgbarkeits-Beschriftung & Datenprotokollierung",
            "trigger": "requirements.traceability_required",
            "action": "add_or_enforce marking and data_logging operations",
            "description_en": "Individual traceability requires laser marking + code verification + database interface.",
            "description_de": "Individuelle Rueckverfolgbarkeit erfordert Laserbeschriftung + Code-Verifikation + Datenbankschnittstelle.",
            "priority": 3,
        },
        {
            "id": "medical_inspection",
            "name_en": "Medical 100% Inspection Enforcement",
            "name_de": "Medizinische 100%-Inspektion-Zwang",
            "trigger": "product.category == 'medical'",
            "action": "enforce inspection.required = True",
            "description_en": "Medical products must have 100% inspection per regulatory requirements (ISO 13485, FDA).",
            "description_de": "Medizinprodukte muessen gemaess regulatorischer Anforderungen 100% geprueft werden (ISO 13485, FDA).",
            "priority": 4,
        },
        {
            "id": "spring_testing",
            "name_en": "Spring Mechanism Testing",
            "name_de": "Feder-Mechanismus-Pruefung",
            "trigger": "'spring' in product.typical_parts_list",
            "action": "add_or_enforce testing operation with force-displacement test",
            "description_en": "Any product with a spring requires force-displacement testing and preload station to verify function.",
            "description_de": "Jedes Produkt mit Feder erfordert Kraft-Weg-Pruefung und Vorspannstation zur Funktionsverifikation.",
            "priority": 5,
        },
        {
            "id": "packaging_enforcement",
            "name_en": "Packaging Enforcement",
            "name_de": "Verpackungs-Zwang",
            "trigger": "requirements.packaging_required",
            "action": "add_or_enforce packaging operation",
            "description_en": "Ensure packaging module is present if customer requires end-of-line packaging.",
            "description_de": "Verpackungsmodul sicherstellen, wenn Kunde End-of-Line-Verpackung verlangt.",
            "priority": 6,
        },
        {
            "id": "cleanroom_filter",
            "name_en": "Cleanroom Module Filter",
            "name_de": "Reinraum-Modul-Filter",
            "trigger": "requirements.cleanroom_required",
            "action": "filter modules to cleanroom_compatible = True only",
            "description_en": "When cleanroom is required, only cleanroom-compatible modules may be selected per ISO 14644-1.",
            "description_de": "Bei Reinraumanforderung duerfen nur reinraum-kompatible Module ausgewaehlt werden gemaess ISO 14644-1.",
            "priority": 7,
        },
        {
            "id": "global_safety",
            "name_en": "Global Safety & Control",
            "name_de": "Globale Sicherheit & Steuerung",
            "trigger": "always",
            "action": "add control (PLC) and hmi operations if not present",
            "description_en": "Every production line must have a PLC control cabinet and HMI operator station per machinery directive.",
            "description_de": "Jede Produktionslinie benoetigt SPS-Schaltschrank und HMI-Bedienstation gemaess Maschinenrichtlinie.",
            "priority": 8,
        }
    ]

    # ═══════════════════════════════════════════════════════════════════
    # 5. ARCHITECTURE SELECTION RULES
    # ═══════════════════════════════════════════════════════════════════
    ARCHITECTURE_RULES = [
        {
            "id": "high_throughput",
            "name_en": "High Throughput → Linear Transport",
            "name_de": "Hoher Durchsatz → Linear-Transportsystem",
            "condition": "nominal_rate >= 100",
            "architecture": "linear_transport_system",
            "name": "Linear Transport System (High Throughput)",
            "reason_en": "High throughput (>100 ppm) requires linear transport system for parallel processing stations with independent cycle times.",
            "reason_de": "Hoher Durchsatz (>100 ppm) erfordert Linear-Transportsystem fuer parallele Bearbeitungsstationen mit unabhaengigen Taktzeiten.",
            "priority": 1,
        },
        {
            "id": "medium_throughput",
            "name_en": "Medium Throughput → Pallet Conveyor",
            "name_de": "Mittlerer Durchsatz → Paletten-Foerderer",
            "condition": "50 <= nominal_rate < 100",
            "architecture": "pallet_conveyor",
            "name": "Pallet Conveyor (Medium Throughput)",
            "reason_en": "Medium throughput (50–100 ppm) is optimal for pallet conveyor with buffer stations and pallet-based part carriers.",
            "reason_de": "Mittlerer Durchsatz (50–100 ppm) ist optimal fuer Paletten-Foerderer mit Pufferstationen und paletten-basierten Teiltraegern.",
            "priority": 2,
        },
        {
            "id": "low_throughput",
            "name_en": "Low Throughput → Rotary Indexing",
            "name_de": "Niedriger Durchsatz → Rundtakt-Tisch",
            "condition": "nominal_rate < 50",
            "architecture": "rotary_indexing_table",
            "name": "Rotary Indexing Table (Compact / Low Throughput)",
            "reason_en": "Low throughput (<50 ppm) favors compact rotary indexing table for synchronous processing and minimal footprint.",
            "reason_de": "Niedriger Durchsatz (<50 ppm) bevorzugt kompakten Rundtakt-Tisch fuer synchrone Bearbeitung und minimalen Fußabdruck.",
            "priority": 3,
        },
        {
            "id": "high_variants",
            "name_en": "High Variants → Hybrid Flexible",
            "name_de": "Hohe Variantenzahl → Hybrid-Flexibles System",
            "condition": "variants >= 5",
            "architecture": "hybrid_flexible",
            "name": "Hybrid Flexible System (Robot + Flexible Feeders)",
            "reason_en": "High variant complexity (>=5 SKUs) requires hybrid flexible system with robot cells and flexible feeders for quick changeover.",
            "reason_de": "Hohe Variantenkomplexitaet (>=5 SKUs) erfordert hybrides flexibles System mit Roboterzellen und flexiblen Zufuehrsystemen fuer schnellen Umruestung.",
            "priority": 0,  # Overrides throughput rules
        },
        {
            "id": "footprint_constraint",
            "name_en": "Footprint Constraint → Rotary",
            "name_de": "Footprint-Beschraenkung → Rundtakt",
            "condition": "total_footprint > footprint_max * 0.8",
            "architecture": "rotary_indexing_table",
            "name": "Rotary Indexing Table (Footprint Optimized)",
            "reason_en": "Footprint constraint (>80% of max) triggered rotary indexing table selection for compact, space-efficient layout.",
            "reason_de": "Footprint-Beschraenkung (>80% des Max) loeste Auswahl von Rundtakt-Tisch fuer kompaktes, platzsparendes Layout aus.",
            "priority": 0,  # Overrides throughput rules
        }
    ]

    # ═══════════════════════════════════════════════════════════════════
    # 6. RECOMMENDATION ENGINE (Deterministic, No AI)
    # ═══════════════════════════════════════════════════════════════════
    # For each warning type, the Knowledge Model provides deterministic
    # engineering recommendations based on first principles.

    RECOMMENDATIONS = {
        "capacity_utilization_low": {
            "condition": "capacity_utilization < 0.30",
            "severity": "warning",
            "recommendations_en": [
                "Consider reducing the number of parallel stations to save capital expenditure.",
                "Evaluate whether a single-station rotary indexing table would suffice instead of a linear system.",
                "If future demand growth is expected, the current over-specification provides headroom.",
                "Re-evaluate the OEE target — a lower target may be more realistic and reduce line complexity.",
            ],
            "recommendations_de": [
                "Erwaeigen Sie die Reduzierung der Anzahl paralleler Stationen, um Kapitalkosten zu sparen.",
                "Bewerten Sie, ob ein einzelner Rundtakt-Tisch statt eines Linear-Systems ausreichen wuerde.",
                "Wenn zukuenftige Nachfragesteigerung erwartet wird, bietet die aktuelle Ueberspezifikation Spielraum.",
                "Ueberpruefen Sie das OEE-Ziel neu — ein niedrigeres Ziel koennte realistischer sein und die Linienkomplexitaet reduzieren.",
            ],
        },
        "capacity_utilization_high": {
            "condition": "capacity_utilization > 0.95",
            "severity": "warning",
            "recommendations_en": [
                "CRITICAL: The line is operating at >95% capacity. Any downtime will cause missed deliveries.",
                "Recommend adding a third shift or increasing the nominal output rate target.",
                "Consider duplicating bottleneck stations (testing, insertion) to increase throughput.",
                "Evaluate whether a buffer station can absorb short-term disruptions.",
            ],
            "recommendations_de": [
                "KRITISCH: Die Linie arbeitet bei >95% Kapazitaet. Jeder Ausfall fuehrt zu verpassten Lieferungen.",
                "Empfohlen: Dritte Schicht hinzufuegen oder Nenn-Ausgaberate-Ziel erhoehen.",
                "Erwaeigen Sie die Duplizierung von Engpassstationen (Pruefung, Einfuegen) zur Durchsatzerhoehung.",
                "Bewerten Sie, ob eine Pufferstation kurzfristige Stoerungen absorbieren kann.",
            ],
        },
        "cost_overrun": {
            "condition": "total_cost > budget_max",
            "severity": "error",
            "recommendations_en": [
                "Reduce the number of parallel stations by accepting a slightly higher takt time.",
                "Switch optimization priority to 'cost' to select lower-cost modules.",
                "Evaluate whether some operations can be combined (e.g., test + inspect in one station).",
                "Consider a rotary indexing table instead of linear transport to reduce transport system cost.",
                "Remove optional operations (marking, data logging) if not strictly required.",
            ],
            "recommendations_de": [
                "Reduzieren Sie die Anzahl paralleler Stationen, indem Sie eine leicht hoehere Taktzeit akzeptieren.",
                "Wechseln Sie die Optimierungsprioritaet zu 'Kosten', um kostenguenstigere Module auszuwaehlen.",
                "Bewerten Sie, ob einige Operationen kombiniert werden koennen (z.B. Pruefung + Inspektion in einer Station).",
                "Erwaeigen Sie einen Rundtakt-Tisch statt Linear-Transport, um Transportsystemkosten zu senken.",
                "Entfernen Sie optionale Operationen (Beschriftung, Datenprotokollierung), wenn nicht strikt erforderlich.",
            ],
        },
        "footprint_overrun": {
            "condition": "total_footprint > footprint_max",
            "severity": "error",
            "recommendations_en": [
                "Switch to a rotary indexing table — it is the most compact transport architecture.",
                "Reduce the number of parallel stations by selecting higher-capacity modules.",
                "Switch optimization priority to 'footprint' to minimize floor space.",
                "Consider vertical stacking of modules if ceiling height permits.",
                "Evaluate whether the production floor space constraint can be relaxed.",
            ],
            "recommendations_de": [
                "Wechseln Sie zu einem Rundtakt-Tisch — es ist die kompakteste Transportarchitektur.",
                "Reduzieren Sie die Anzahl paralleler Stationen durch Auswahl hoeherer Kapazitaetsmodule.",
                "Wechseln Sie die Optimierungsprioritaet zu 'Fußabdruck', um Bodenflaeche zu minimieren.",
                "Erwaeigen Sie vertikales Stapeln von Modulen, wenn die Deckenhoehe es erlaubt.",
                "Bewerten Sie, ob die Produktionsflaechenbeschraenkung gelockert werden kann.",
            ],
        },
        "no_module_found": {
            "condition": "any step has NO_MODULE_FOUND",
            "severity": "error",
            "recommendations_en": [
                "The tolerance requirement may be too strict. Consider relaxing the tolerance (µm) value.",
                "If cleanroom is required, verify that the product category actually needs it.",
                "The variant count may exceed available module flexibility. Reduce variants or use flexible feeders.",
                "Consider adding a custom module to the database for this specific operation.",
            ],
            "recommendations_de": [
                "Die Toleranzanforderung koennte zu streng sein. Erwaeigen Sie eine Lockerung des Toleranzwerts (µm).",
                "Wenn Reinraum erforderlich ist, verifizieren Sie, ob die Produktkategorie ihn tatsaechlich benoetigt.",
                "Die Variantenzahl koennte die verfuegbare Modulflexibilitaet ueberschreiten. Reduzieren Sie Varianten oder verwenden Sie flexible Zufuehrer.",
                "Erwaeigen Sie das Hinzufuegen eines benutzerdefinierten Moduls zur Datenbank fuer diese spezifische Operation.",
            ],
        },
        "takt_time_critical": {
            "condition": "takt_time < 0.5",
            "severity": "warning",
            "recommendations_en": [
                "Takt time is very short (<0.5s). High-speed linear transport with dedicated fast-cycle stations is required.",
                "Consider splitting the operation into multiple parallel stations to reduce per-station cycle time.",
                "Evaluate whether the output rate target can be reduced or OEE improved through preventive maintenance.",
            ],
            "recommendations_de": [
                "Taktzeit ist sehr kurz (<0,5s). Hochgeschwindigkeits-Linear-Transport mit dedizierten Schnellzyklus-Stationen ist erforderlich.",
                "Erwaeigen Sie die Aufteilung der Operation in mehrere parallele Stationen, um die Taktzeit pro Station zu reduzieren.",
                "Bewerten Sie, ob das Ausgaberate-Ziel reduziert oder OEE durch praeventive Wartung verbessert werden kann.",
            ],
        },
        "bottleneck_detected": {
            "condition": "any module effective_cycle_time > takt_time * 1.2",
            "severity": "warning",
            "recommendations_en": [
                "A bottleneck station has been detected. The effective module cycle time (raw cycle / parallel units) exceeds the takt time buffer.",
                "Add parallel stations for the bottleneck operation to balance the line.",
                "Consider upgrading to a higher-capacity module for the bottleneck step.",
                "Evaluate whether the operation can be split into pre- and post-processing steps.",
            ],
            "recommendations_de": [
                "Eine Engpassstation wurde erkannt. Die effektive Modulzykluszeit (Rohzyklus / parallele Einheiten) ueberschreitet den Taktzeit-Puffer.",
                "Fuegen Sie parallele Stationen fuer die Engpassoperation hinzu, um die Linie zu balancieren.",
                "Erwaeigen Sie ein Upgrade auf ein hoeherkapazitaetsmodul fuer den Engpassschritt.",
                "Bewerten Sie, ob die Operation in Vor- und Nachbearbeitungsschritte aufgeteilt werden kann.",
            ],
        },
        "energy_high": {
            "condition": "total_energy / nominal_rate > 0.5 kW/ppm",
            "severity": "warning",
            "recommendations_en": [
                "Energy consumption is high relative to throughput. Consider selecting lower-energy modules.",
                "Evaluate whether all parallel stations need to run simultaneously or can be staged.",
                "Switch optimization priority to 'energy' to prefer energy-efficient modules.",
            ],
            "recommendations_de": [
                "Der Energieverbrauch ist im Verhaeltnis zum Durchsatz hoch. Erwaeigen Sie energiesparendere Module.",
                "Pruefen Sie, ob alle parallelen Stationen gleichzeitig laufen muessen oder gestaffelt werden koennen.",
                "Wechseln Sie die Optimierungsprioritaet zu 'Energie', um energieeffiziente Module zu bevorzugen.",
            ],
        },
        "too_many_parallel": {
            "condition": "parallel_units > 4",
            "severity": "warning",
            "recommendations_en": [
                "High number of parallel units increases footprint and cost. Consider a higher-capacity module.",
                "Evaluate whether the output rate target can be reduced or OEE improved to reduce parallel count.",
                "A rotary indexing table may be more compact than multiple parallel stations on a linear system.",
            ],
            "recommendations_de": [
                "Eine hohe Anzahl paralleler Einheiten erhoeht Fussabdruck und Kosten. Erwaeigen Sie ein hoeherkapazitaetsmodul.",
                "Pruefen Sie, ob das Ausgaberate-Ziel reduziert oder OEE verbessert werden kann, um die Parallelanzahl zu senken.",
                "Ein Rundtakt-Tisch koennte kompakter sein als mehrere parallele Stationen auf einem Linear-System.",
            ],
        },
        "high_reject_rate": {
            "condition": "reject_rate > 5%",
            "severity": "warning",
            "recommendations_en": [
                "High reject rate inflates nominal rate and cost. Focus on upstream process improvement.",
                "Consider adding in-process inspection stations to catch defects early.",
                "Evaluate whether the assembly tolerance or process parameters can be tightened.",
            ],
            "recommendations_de": [
                "Eine hohe Ausschussrate erhoeht die Nennrate und Kosten. Konzentrieren Sie sich auf Verbesserung des Upstream-Prozesses.",
                "Erwaeigen Sie Inline-Inspektionsstationen, um Fehler frueh zu erkennen.",
                "Pruefen Sie, ob die Montagetoleranz oder Prozessparameter verschaerft werden koennen.",
            ],
        },
    }

    # ═══════════════════════════════════════════════════════════════════
    # 7. LINE BALANCING KNOWLEDGE
    # ═══════════════════════════════════════════════════════════════════
    LINE_BALANCING = {
        "ideal_utilization_range": (0.30, 0.85),
        "takt_time_buffer_factor": 1.2,
        "max_parallel_units_per_station": 4,
        "description_en": "Line balancing ensures each station operates at similar utilization. Bottlenecks occur when one station's cycle time exceeds the takt time.",
        "description_de": "Linienbalancing stellt sicher, dass jede Station mit aehnlicher Auslastung arbeitet. Engpaesse entstehen, wenn eine Station die Taktzeit ueberschreitet.",
    }

    # ═══════════════════════════════════════════════════════════════════
    # 8. KPI FORMULAS (Knowledge Layer)
    # ═══════════════════════════════════════════════════════════════════
    KPI_FORMULAS = {
        "nominal_rate": {
            "symbol": "R_nom",
            "en": "Nominal Rate = Output Rate / (OEE × (1 - Reject Rate))",
            "de": "Nennrate = Ausgaberate / (OEE × (1 - Ausschussrate))",
            "formula": lambda output, oee, reject: output / (oee * (1 - reject)),
            "description_en": "The true production speed the line must achieve, accounting for availability and quality losses.",
            "description_de": "Die tatsaechliche Produktionsgeschwindigkeit, die die Linie erreichen muss, unter Beruecksichtigung von Verfuegbarkeits- und Qualitaetsverlusten.",
        },
        "takt_time": {
            "symbol": "T_takt",
            "en": "Takt Time = 60 / Nominal Rate",
            "de": "Taktzeit = 60 / Nennrate",
            "formula": lambda nominal_rate: 60.0 / nominal_rate,
            "description_en": "Time budget per part. Every module must complete its cycle within this window.",
            "description_de": "Zeitbudget pro Teil. Jedes Modul muss seinen Zyklus innerhalb dieses Fensters abschliessen.",
        },
        "annual_capacity": {
            "symbol": "C_annual",
            "en": "Annual Capacity = Nominal Rate × 60 min × 16 h × 250 days",
            "de": "Jahreskapazitaet = Nennrate × 60 min × 16 h × 250 Tage",
            "formula": lambda nominal_rate: nominal_rate * 60 * 16 * 250,
            "description_en": "Maximum parts per year assuming 2-shift operation, 250 working days.",
            "description_de": "Maximale Teile pro Jahr bei 2-Schicht-Betrieb, 250 Arbeitstagen.",
        },
        "parallel_units": {
            "symbol": "N_par",
            "en": "Parallel Units = ceil(Nominal Rate / Module Capacity)",
            "de": "Parallele Einheiten = ceil(Nennrate / Modulkapazitaet)",
            "formula": lambda nominal_rate, module_capacity: ceil(nominal_rate / module_capacity),
            "description_en": "How many identical modules must run in parallel to meet the takt time.",
            "description_de": "Wie viele identische Module parallel laufen muessen, um die Taktzeit zu erreichen.",
        }
    }

    # ═══════════════════════════════════════════════════════════════════
    # 9. MODULE CATEGORIES
    # ═══════════════════════════════════════════════════════════════════
    MODULE_CATEGORIES = {
        "feeding_systems": {"en": "Feeding Systems", "de": "Zufuehrsysteme"},
        "robot_cells": {"en": "Robot Cells", "de": "Roboterzellen"},
        "transport_systems": {"en": "Transport Systems", "de": "Transportsysteme"},
        "press_systems": {"en": "Press Systems", "de": "Presssysteme"},
        "joining_systems": {"en": "Joining Systems", "de": "Fuegesysteme"},
        "dosing_systems": {"en": "Dosing Systems", "de": "Dosiersysteme"},
        "inspection_systems": {"en": "Inspection Systems", "de": "Inspektionssysteme"},
        "testing_systems": {"en": "Testing Systems", "de": "Pruefsysteme"},
        "marking_systems": {"en": "Marking Systems", "de": "Beschriftungssysteme"},
        "packaging_systems": {"en": "Packaging Systems", "de": "Verpackungssysteme"},
        "quality_handling": {"en": "Quality Handling", "de": "Qualitaets-Handling"},
        "control_systems": {"en": "Control Systems", "de": "Steuerungssysteme"},
        "assembly_systems": {"en": "Assembly Systems", "de": "Montagesysteme"},
    }

    # ═══════════════════════════════════════════════════════════════════
    # 10. OPTIMIZATION PRIORITIES
    # ═══════════════════════════════════════════════════════════════════
    OPTIMIZATION_PRIORITIES = {
        "cost": {
            "en": "Lowest Total Cost",
            "de": "Niedrigste Gesamtkosten",
            "weights": {"cost": 0.5, "footprint": 0.2, "energy": 0.2, "flexibility": 0.1},
            "description_en": "Prioritize minimizing total capital expenditure (CAPEX).",
            "description_de": "Priorisierung der Minimierung der Gesamtkapitalkosten (CAPEX).",
        },
        "footprint": {
            "en": "Smallest Floor Space",
            "de": "Kleinster Fussabdruck",
            "weights": {"cost": 0.2, "footprint": 0.5, "energy": 0.2, "flexibility": 0.1},
            "description_en": "Prioritize minimizing production floor space usage.",
            "description_de": "Priorisierung der Minimierung der Produktionsflaechennutzung.",
        },
        "energy": {
            "en": "Lowest Energy Consumption",
            "de": "Niedrigster Energieverbrauch",
            "weights": {"cost": 0.2, "footprint": 0.2, "energy": 0.5, "flexibility": 0.1},
            "description_en": "Prioritize minimizing total energy consumption (OPEX).",
            "description_de": "Priorisierung der Minimierung des Gesamtenergieverbrauchs (OPEX).",
        },
        "flexibility": {
            "en": "Highest Flexibility",
            "de": "Hoechste Flexibilitaet",
            "weights": {"cost": 0.1, "footprint": 0.1, "energy": 0.1, "flexibility": 0.7},
            "description_en": "Prioritize maximum flexibility for future product variants and changeover time.",
            "description_de": "Priorisierung maximaler Flexibilitaet fuer zukuenftige Produktvarianten und Umruestzeit.",
        }
    }

    # ═══════════════════════════════════════════════════════════════════
    # INSTANCE METHODS
    # ═══════════════════════════════════════════════════════════════════

    def __init__(self):
        self._capability_map = self._build_capability_map()

    def _build_capability_map(self) -> Dict[str, List[str]]:
        mapping = {}
        for op_type, op_data in self.OPERATIONS.items():
            for tag in op_data["capability_tags"]:
                if tag not in mapping:
                    mapping[tag] = []
                mapping[tag].append(op_type)
        return mapping

    def get_operation_for_tags(self, tags: List[str]) -> Optional[str]:
        for tag in tags:
            if tag in self._capability_map:
                return self._capability_map[tag][0]
        return None

    def get_capability_tags(self, operation_type: str) -> List[str]:
        return self.OPERATIONS.get(operation_type, {}).get("capability_tags", [operation_type])

    def get_domain_rules(self) -> List[Dict[str, Any]]:
        return sorted(self.DOMAIN_RULES, key=lambda r: r["priority"])

    def get_architecture_rules(self) -> List[Dict[str, Any]]:
        return sorted(self.ARCHITECTURE_RULES, key=lambda r: r["priority"])

    def get_optimization_weights(self, priority: str) -> Dict[str, float]:
        return self.OPTIMIZATION_PRIORITIES.get(priority, {}).get("weights", 
            {"cost": 0.25, "footprint": 0.25, "energy": 0.25, "flexibility": 0.25})

    def get_kpi_description(self, kpi_name: str, lang: str = "en") -> str:
        kpi = self.KPI_FORMULAS.get(kpi_name, {})
        return kpi.get(f"description_{lang}", kpi.get("description_en", ""))

    def get_product_category_info(self, category: str, lang: str = "en") -> Dict[str, Any]:
        info = self.PRODUCT_CATEGORIES.get(category, {})
        return {
            "description": info.get(f"description_{lang}", info.get("description_en", "")),
            "default_cleanroom": info.get("default_cleanroom", False),
            "inspection_enforced": info.get("inspection_enforced", False),
            "typical_tolerance_um": info.get("typical_tolerance_um", 100),
            "preferred_feeder": info.get("preferred_feeder", "bowl_feeder"),
            "preferred_transport": info.get("preferred_transport", "pallet_conveyor"),
            "notes": info.get(f"notes_{lang}", info.get("notes_en", "")),
        }

    def get_operation_info(self, operation_type: str, lang: str = "en") -> Dict[str, Any]:
        op = self.OPERATIONS.get(operation_type, {})
        return {
            "name": op.get(f"{lang}", op.get("en", operation_type)),
            "description": op.get(f"description_{lang}", op.get("description_en", "")),
            "capability_tags": op.get("capability_tags", []),
            "typical_cycle_s": op.get("typical_cycle_s", 1.0),
            "is_bottleneck_prone": op.get("is_bottleneck_prone", False),
        }

    def get_module_category_name(self, category: str, lang: str = "en") -> str:
        cat = self.MODULE_CATEGORIES.get(category, {})
        return cat.get(lang, cat.get("en", category))

    def get_optimization_info(self, priority: str, lang: str = "en") -> Dict[str, Any]:
        opt = self.OPTIMIZATION_PRIORITIES.get(priority, {})
        return {
            "name": opt.get(lang, opt.get("en", priority)),
            "description": opt.get(f"description_{lang}", opt.get("description_en", "")),
            "weights": opt.get("weights", {}),
        }

    def get_recommendations(self, warning_type: str, lang: str = "en") -> List[str]:
        """Get deterministic recommendations for a warning type."""
        rec = self.RECOMMENDATIONS.get(warning_type, {})
        return rec.get(f"recommendations_{lang}", rec.get("recommendations_en", []))

    def get_all_recommendations_for_report(self, report: Dict[str, Any], lang: str = "en") -> List[Dict[str, Any]]:
        """Analyze report and generate all applicable recommendations."""
        recommendations = []
        kpis = report.get("kpis", {})
        cost = report.get("cost_summary", {})
        feasibility = report.get("feasibility", {})
        process_chain = report.get("process_chain", [])
        input_req = report.get("input", {})
        
        util = kpis.get("capacity_utilization", 0)
        takt = kpis.get("takt_time_s", 999)
        
        # Check capacity utilization
        if util < 0.30:
            recommendations.append({
                "type": "capacity_utilization_low",
                "severity": "warning",
                "title_en": "Line Over-Specified",
                "title_de": "Linie ueberspezifiziert",
                "message_en": f"Capacity utilization is only {util*100:.1f}%. The line is significantly over-specified for the demand.",
                "message_de": f"Kapazitaetsauslastung betraegt nur {util*100:.1f}%. Die Linie ist fuer den Bedarf deutlich ueberspezifiziert.",
                "actions": self.get_recommendations("capacity_utilization_low", lang),
            })
        elif util > 1.0:
            recommendations.append({
                "type": "capacity_utilization_over",
                "severity": "error",
                "title_en": "Demand Exceeds Line Capacity",
                "title_de": "Bedarf ueberschreitet Linienkapazitaet",
                "message_en": f"Capacity utilization is {util*100:.1f}%. The annual demand exceeds the line's maximum capacity. This configuration is physically impossible.",
                "message_de": f"Kapazitaetsauslastung betraegt {util*100:.1f}%. Der Jahresbedarf ueberschreitet die maximale Linienkapazitaet. Diese Konfiguration ist physikalisch unmoeglich.",
                "actions": self.get_recommendations("capacity_utilization_high", lang),
            })
        elif util > 0.95:
            recommendations.append({
                "type": "capacity_utilization_high",
                "severity": "error",
                "title_en": "Line at Maximum Capacity",
                "title_de": "Linie bei maximaler Kapazitaet",
                "message_en": f"Capacity utilization is {util*100:.1f}%. The line is operating at critical capacity with no buffer.",
                "message_de": f"Kapazitaetsauslastung betraegt {util*100:.1f}%. Die Linie arbeitet bei kritischer Kapazitaet ohne Puffer.",
                "actions": self.get_recommendations("capacity_utilization_high", lang),
            })
        
        # Check takt time
        if takt < 0.5:
            recommendations.append({
                "type": "takt_time_critical",
                "severity": "warning",
                "title_en": "Critical Takt Time",
                "title_de": "Kritische Taktzeit",
                "message_en": f"Takt time is {takt:.3f}s. This is extremely short and requires high-speed equipment.",
                "message_de": f"Taktzeit betraegt {takt:.3f}s. Dies ist extrem kurz und erfordert Hochgeschwindigkeitsausstattung.",
                "actions": self.get_recommendations("takt_time_critical", lang),
            })
        
        # Check cost overrun
        if cost.get("total_cost_eur", 0) > cost.get("budget_max_eur", 999999):
            recommendations.append({
                "type": "cost_overrun",
                "severity": "error",
                "title_en": "Budget Exceeded",
                "title_de": "Budget ueberschritten",
                "message_en": f"Total cost {cost['total_cost_eur']:,.0f} EUR exceeds budget {cost['budget_max_eur']:,.0f} EUR.",
                "message_de": f"Gesamtkosten {cost['total_cost_eur']:,.0f} EUR ueberschreiten Budget {cost['budget_max_eur']:,.0f} EUR.",
                "actions": self.get_recommendations("cost_overrun", lang),
            })
        
        # Check footprint overrun
        if cost.get("total_footprint_m2", 0) > cost.get("footprint_max_m2", 999999):
            recommendations.append({
                "type": "footprint_overrun",
                "severity": "error",
                "title_en": "Footprint Exceeded",
                "title_de": "Fussabdruck ueberschritten",
                "message_en": f"Total footprint {cost['total_footprint_m2']:.1f} m² exceeds limit {cost['footprint_max_m2']:.0f} m².",
                "message_de": f"Gesamtflaeche {cost['total_footprint_m2']:.1f} m² ueberschreitet Limit {cost['footprint_max_m2']:.0f} m².",
                "actions": self.get_recommendations("footprint_overrun", lang),
            })
        
        # Check missing modules with SPECIFIC reason analysis
        no_modules = [s for s in process_chain if s.get("status") == "NO_MODULE_FOUND"]
        if no_modules:
            op_types = [s['operation_type'] for s in no_modules]
            rec = {
                "type": "no_module_found",
                "severity": "error",
                "title_en": "Missing Module",
                "title_de": "Fehlendes Modul",
                "message_en": f"No compatible module found for {len(no_modules)} operation(s): {', '.join(op_types)}.",
                "message_de": f"Kein kompatibles Modul gefunden fuer {len(no_modules)} Operation(en): {', '.join(op_types)}.",
                "actions": self.get_recommendations("no_module_found", lang),
            }
            # Add specific guidance based on input requirements
            if input_req.get("tolerance_um", 0) < 50:
                rec["actions"] = rec["actions"] + (["The tolerance requirement may be too strict. Consider relaxing it."] if lang == "en" else ["Die Toleranzanforderung koennte zu streng sein. Erwaeigen Sie eine Lockerung."])
            if input_req.get("cleanroom_required"):
                rec["actions"] = rec["actions"] + (["Cleanroom requirement is active. Verify if your product category actually needs it."] if lang == "en" else ["Reinraum-Anforderung ist aktiv. Pruefen Sie, ob Ihre Produktkategorie dies tatsaechlich benoetigt."])
            recommendations.append(rec)
        
        # Check bottleneck using EFFECTIVE cycle time (accounting for parallel units)
        # BUG FIX: was comparing raw cycle_time_s to takt, should be cycle_time_s / parallel_units
        for step in process_chain:
            mod = step.get("module")
            if mod:
                raw_cycle = mod.get("cycle_time_s", 0)
                parallel = max(mod.get("parallel_units", 1), 1)
                effective_cycle = raw_cycle / parallel
                if effective_cycle > takt * 1.2:
                    recommendations.append({
                        "type": "bottleneck_detected",
                        "severity": "warning",
                        "title_en": "Bottleneck Detected",
                        "title_de": "Engpass erkannt",
                        "message_en": f"Module '{mod['name']}' effective cycle time ({effective_cycle:.3f}s = {raw_cycle}s / {parallel} units) exceeds takt buffer ({takt*1.2:.3f}s).",
                        "message_de": f"Modul '{mod['name']}' effektive Zykluszeit ({effective_cycle:.3f}s = {raw_cycle}s / {parallel} Einheiten) ueberschreitet Takt-Puffer ({takt*1.2:.3f}s).",
                        "actions": self.get_recommendations("bottleneck_detected", lang),
                    })
        
        # Check energy efficiency
        total_energy = cost.get("total_energy_kw", 0)
        nominal_rate = kpis.get("nominal_rate_ppm", 1)
        if total_energy > 0 and (total_energy / nominal_rate) > 0.5:
            recommendations.append({
                "type": "energy_high",
                "severity": "warning",
                "title_en": "High Energy Consumption",
                "title_de": "Hoher Energieverbrauch",
                "message_en": f"Energy consumption is {total_energy:.2f} kW for {nominal_rate:.0f} ppm. Consider energy-efficient modules.",
                "message_de": f"Energieverbrauch betraegt {total_energy:.2f} kW bei {nominal_rate:.0f} Teile/min. Erwaeigen Sie energieeffiziente Module.",
                "actions": self.get_recommendations("energy_high", lang),
            })
        
        # Check excessive parallel units (inefficiency indicator)
        for step in process_chain:
            mod = step.get("module")
            if mod and mod.get("parallel_units", 1) > 4:
                recommendations.append({
                    "type": "too_many_parallel",
                    "severity": "warning",
                    "title_en": "High Parallel Unit Count",
                    "title_de": "Hohe Anzahl paralleler Einheiten",
                    "message_en": f"Module '{mod['name']}' uses {mod['parallel_units']} parallel units. Consider a higher-capacity module to reduce footprint.",
                    "message_de": f"Modul '{mod['name']}' verwendet {mod['parallel_units']} parallele Einheiten. Erwaeigen Sie ein hoeherkapazitaetsmodul zur Reduzierung des Fussabdrucks.",
                    "actions": self.get_recommendations("too_many_parallel", lang),
                })
        
        # Check reject rate impact
        reject_rate = kpis.get("reject_rate", 0)
        if reject_rate > 0.05:
            recommendations.append({
                "type": "high_reject_rate",
                "severity": "warning",
                "title_en": "High Reject Rate Impact",
                "title_de": "Hoher Ausschussraten-Einfluss",
                "message_en": f"Reject rate is {reject_rate*100:.1f}%. This significantly inflates the required nominal rate and cost.",
                "message_de": f"Ausschussrate betraegt {reject_rate*100:.1f}%. Dies erhoeht die erforderliche Nennrate und Kosten erheblich.",
                "actions": self.get_recommendations("high_reject_rate", lang),
            })
        
        return recommendations

    def get_transfer_function(self, name: str) -> Dict[str, Any]:
        """Get a transfer function by name."""
        return self.TRANSFER_FUNCTIONS.get(name, {})

    def get_line_balancing_info(self, lang: str = "en") -> Dict[str, Any]:
        """Get line balancing knowledge."""
        lb = self.LINE_BALANCING
        return {
            "ideal_range": lb["ideal_utilization_range"],
            "buffer_factor": lb["takt_time_buffer_factor"],
            "max_parallel": lb["max_parallel_units_per_station"],
            "description": lb.get(f"description_{lang}", lb.get("description_en", "")),
        }


# Singleton instance
KNOWLEDGE_MODEL = KnowledgeModel()
