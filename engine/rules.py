from typing import Dict, Any, List, Tuple

# Canonical order of operations in a special-purpose machine line
# This ensures that operations injected by rules are positioned correctly
# in the process sequence, not appended at the end.
CANONICAL_ORDER = {
    "feeding": 1,
    "assembly": 2,
    "insertion": 3,
    "testing": 4,
    "inspection": 5,
    "marking": 6,
    "packaging": 7,
    "reject": 8,
    "control": 9,
    "hmi": 10,
    "data_logging": 11,
}

def _get_op_priority(op_type: str) -> int:
    """Return the canonical priority for an operation type. Unknown types go last."""
    return CANONICAL_ORDER.get(op_type, 99)

def apply_rules(requirements: Dict[str, Any], product: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Apply deterministic rules in fixed order.
    After all rules are applied, operations are sorted into canonical order
    and renumbered sequentially to ensure correct process sequence.
    Returns (augmented_operations, rule_trace).
    """
    operations = [dict(op) for op in product["base_operations"]]
    trace = []

    # Rule 1: Product rules (default cleanroom)
    if product["default_cleanroom_requirement"] and not requirements.get("cleanroom_required"):
        requirements["cleanroom_required"] = True
        trace.append(f"PRODUCT_RULE: {product['name']} enforces cleanroom requirement.")

    # Rule 2: Customer requirement rules (inspection)
    if requirements.get("inspection_required"):
        has_inspection = any(op["operation_type"] == "inspection" for op in operations)
        if not has_inspection:
            operations.append({
                "step": 99,
                "operation_type": "inspection",
                "required": True,
                "notes": "Added by customer inspection requirement"
            })
            trace.append("CUSTOMER_RULE: Inspection required -> added vision inspection module.")
        else:
            for op in operations:
                if op["operation_type"] == "inspection":
                    op["required"] = True
            trace.append("CUSTOMER_RULE: Inspection required -> existing inspection step enforced.")

    # Rule 3: Traceability rules
    if requirements.get("traceability_required"):
        has_marking = any(op["operation_type"] == "marking" for op in operations)
        if not has_marking:
            operations.append({
                "step": 99,
                "operation_type": "marking",
                "required": True,
                "notes": "Added by traceability requirement"
            })
            trace.append("TRACEABILITY_RULE: Individual traceability -> added laser marking + code verification.")
        else:
            for op in operations:
                if op["operation_type"] == "marking":
                    op["required"] = True
            trace.append("TRACEABILITY_RULE: Individual traceability -> marking step enforced.")
        # Add data logging if not present
        has_data = any(op["operation_type"] == "data_logging" for op in operations)
        if not has_data:
            operations.append({
                "step": 99,
                "operation_type": "data_logging",
                "required": True,
                "notes": "Database interface for traceability"
            })
            trace.append("TRACEABILITY_RULE: Added data logging interface for database connectivity.")

    # Rule 4: Inspection rules (medical enforces 100%)
    if product["category"] == "medical":
        for op in operations:
            if op["operation_type"] == "inspection":
                op["required"] = True
        trace.append("INSPECTION_RULE: Medical product -> enforced 100% inspection.")

    # Rule 5: Testing rules (spring mechanism)
    if "spring" in product.get("typical_parts_list", []):
        has_force_test = any(op["operation_type"] == "testing" for op in operations)
        if not has_force_test:
            operations.append({
                "step": 99,
                "operation_type": "testing",
                "required": True,
                "notes": "Force-displacement test for spring mechanism"
            })
            trace.append("TESTING_RULE: Spring mechanism detected -> added force-displacement test + preload station.")
        else:
            for op in operations:
                if op["operation_type"] == "testing":
                    op["required"] = True
            trace.append("TESTING_RULE: Spring mechanism detected -> testing step enforced.")

    # Rule 6: Packaging rules
    if requirements.get("packaging_required"):
        has_packaging = any(op["operation_type"] == "packaging" for op in operations)
        if not has_packaging:
            operations.append({
                "step": 99,
                "operation_type": "packaging",
                "required": True,
                "notes": "Added by packaging requirement"
            })
            trace.append("PACKAGING_RULE: Packaging required -> added packaging module.")
        else:
            for op in operations:
                if op["operation_type"] == "packaging":
                    op["required"] = True
            trace.append("PACKAGING_RULE: Packaging required -> existing packaging step enforced.")

    # Rule 7: Cleanroom constraints
    if requirements.get("cleanroom_required"):
        trace.append("CLEANROOM_RULE: Cleanroom required -> only cleanroom-compatible modules allowed.")

    # Rule 8: Global safety/control rules
    has_control = any(op["operation_type"] == "control" for op in operations)
    if not has_control:
        operations.append({
            "step": 99,
            "operation_type": "control",
            "required": True,
            "notes": "PLC control cabinet (global safety rule)"
        })
        trace.append("GLOBAL_RULE: Added PLC control cabinet for safety and control logic.")
    has_hmi = any(op["operation_type"] == "hmi" for op in operations)
    if not has_hmi:
        operations.append({
            "step": 99,
            "operation_type": "hmi",
            "required": True,
            "notes": "HMI station (global safety rule)"
        })
        trace.append("GLOBAL_RULE: Added HMI station for operator interface.")

    # Sort operations by canonical order and renumber sequentially
    operations.sort(key=lambda op: _get_op_priority(op["operation_type"]))
    for i, op in enumerate(operations, 1):
        op["step"] = i

    return operations, trace
