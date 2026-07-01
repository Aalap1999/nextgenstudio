import json
import os
import re
import logging
import functools

try:
    from jsonschema import validate, ValidationError
except ImportError:
    validate = None
    class ValidationError(Exception):
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEMA_DIR = os.path.join(DATA_DIR, "schemas")

logger = logging.getLogger("smart_machine_studio")

__all__ = [
    "load_json", "load_and_validate_modules", "load_and_validate_products",
    "validate_customer_requirements", "ValidationError", "_validate_module_item"
]

def load_json(path: str) -> dict:
    """Load JSON with robust error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.error("File not found: %s", path)
        raise ValidationError(f"File not found: {path}") from e
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", path, e)
        raise ValidationError(f"Invalid JSON in {path}: {e}") from e
    except PermissionError as e:
        logger.error("Permission denied: %s", path)
        raise ValidationError(f"Permission denied: {path}") from e

def _validate_module_item(m: dict) -> None:
    required = ["id", "name", "category", "cycle_time_s", "capacity_ppm",
                "footprint_m2", "cost_eur", "energy_kw", "flexibility_score",
                "supported_industries", "capability_tags", "cleanroom_compatible",
                "tolerance_um", "variant_flexibility"]
    missing = [k for k in required if k not in m]
    if missing:
        raise ValidationError(f"Module missing fields: {missing}")
    # Sanitize ID format
    if not re.match(r'^[a-zA-Z0-9_\-]+$', str(m.get("id", ""))):
        raise ValidationError(f"Module ID must contain only letters, numbers, underscores, and hyphens")
    for k in ["cycle_time_s", "capacity_ppm", "footprint_m2", "cost_eur", "energy_kw", "tolerance_um"]:
        if not isinstance(m[k], (int, float)) or m[k] < 0:
            raise ValidationError(f"Module {m['id']}: {k} must be >= 0")
    for k in ["flexibility_score", "variant_flexibility"]:
        if not isinstance(m[k], int) or not (1 <= m[k] <= 10):
            raise ValidationError(f"Module {m['id']}: {k} must be 1-10")
    if not isinstance(m["supported_industries"], list) or not all(isinstance(x, str) for x in m["supported_industries"]):
        raise ValidationError(f"Module {m['id']}: supported_industries must be list of strings")
    if not isinstance(m["capability_tags"], list) or not all(isinstance(x, str) for x in m["capability_tags"]):
        raise ValidationError(f"Module {m['id']}: capability_tags must be list of strings")
    if not isinstance(m["cleanroom_compatible"], bool):
        raise ValidationError(f"Module {m['id']}: cleanroom_compatible must be bool")

def _validate_product_item(p: dict) -> None:
    required = ["id", "name", "category", "default_cleanroom_requirement", "typical_parts_list", "base_operations"]
    missing = [k for k in required if k not in p]
    if missing:
        raise ValidationError(f"Product missing fields: {missing}")
    if not isinstance(p["typical_parts_list"], list) or not all(isinstance(x, str) for x in p["typical_parts_list"]):
        raise ValidationError(f"Product {p['id']}: typical_parts_list must be list of strings")
    for op in p["base_operations"]:
        op_req = ["step", "operation_type", "required"]
        op_missing = [k for k in op_req if k not in op]
        if op_missing:
            raise ValidationError(f"Product {p['id']}: operation missing fields {op_missing}")
        if not isinstance(op["step"], int) or op["step"] < 1:
            raise ValidationError(f"Product {p['id']}: step must be >= 1")
        if not isinstance(op["required"], bool):
            raise ValidationError(f"Product {p['id']}: required must be bool")

def validate_modules(data: dict) -> None:
    if validate is not None:
        schema = load_json(os.path.join(SCHEMA_DIR, "module_schema.json"))
        validate(instance=data, schema=schema)
    else:
        if "modules" not in data or not isinstance(data["modules"], list):
            raise ValidationError("modules must be a list")
        for m in data["modules"]:
            _validate_module_item(m)

def validate_products(data: dict) -> None:
    if validate is not None:
        schema = load_json(os.path.join(SCHEMA_DIR, "product_schema.json"))
        validate(instance=data, schema=schema)
    else:
        if "products" not in data or not isinstance(data["products"], list):
            raise ValidationError("products must be a list")
        for p in data["products"]:
            _validate_product_item(p)

@functools.lru_cache(maxsize=1)
def _load_modules_cached() -> dict:
    """Cached module loading to avoid repeated file I/O."""
    path = os.path.join(DATA_DIR, "modules.json")
    data = load_json(path)
    validate_modules(data)
    logger.info("Loaded and validated %d modules", len(data.get("modules", [])))
    return data

@functools.lru_cache(maxsize=1)
def _load_products_cached() -> dict:
    """Cached product loading to avoid repeated file I/O."""
    path = os.path.join(DATA_DIR, "products.json")
    data = load_json(path)
    validate_products(data)
    logger.info("Loaded and validated %d products", len(data.get("products", [])))
    return data

def load_and_validate_modules() -> dict:
    return _load_modules_cached()

def load_and_validate_products() -> dict:
    return _load_products_cached()

def validate_customer_requirements(req: dict) -> None:
    required = [
        "product_type", "output_ppm", "annual_demand", "oee_target",
        "reject_rate", "variants", "tolerance_um", "cleanroom_required",
        "inspection_required", "traceability_required", "packaging_required",
        "footprint_max_m2", "budget_max_eur", "optimization_priority"
    ]
    missing = [k for k in required if k not in req]
    if missing:
        raise ValidationError(f"Missing customer requirement fields: {missing}")
    if req["output_ppm"] <= 0:
        raise ValidationError("output_ppm must be > 0")
    if not (0 < req["oee_target"] <= 1):
        raise ValidationError("oee_target must be in (0, 1]")
    if not (0 <= req["reject_rate"] < 1):
        raise ValidationError("reject_rate must be in [0, 1)")
    if not (1 <= req["variants"] <= 100):
        raise ValidationError("variants must be between 1 and 100")
    if req["tolerance_um"] <= 0:
        raise ValidationError("tolerance_um must be > 0")
    if req["footprint_max_m2"] <= 0:
        raise ValidationError("footprint_max_m2 must be > 0")
    if req["budget_max_eur"] <= 0:
        raise ValidationError("budget_max_eur must be > 0")
    if req["optimization_priority"] not in {"cost", "footprint", "energy", "flexibility"}:
        raise ValidationError("optimization_priority must be one of: cost, footprint, energy, flexibility")
    # Optional operating schedule validation
    if "shifts_per_day" in req and not (1 <= req["shifts_per_day"] <= 3):
        raise ValidationError("shifts_per_day must be between 1 and 3")
    if "hours_per_shift" in req and not (1 <= req["hours_per_shift"] <= 24):
        raise ValidationError("hours_per_shift must be between 1 and 24")
    if "working_days_per_year" in req and not (1 <= req["working_days_per_year"] <= 365):
        raise ValidationError("working_days_per_year must be between 1 and 365")
