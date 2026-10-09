"""Slicer identity: which codes are slicers, which model a row names, which materials are line parts.

Slicers are the machine itself. Their hours come from the machine line catalog
(equipment_catalog, keyed by machine_type), so the maintenance draft never
prices a slicer component as a module. These helpers answer three questions:
"is this type code a slicer?", "which slicer model is this row?" and "is this
material part of the machine line?" (see is_line_part). Model extraction never
guesses: when the dictionary is ambiguous the answer is None.
"""
import re


# Component type codes whose row is a slicer, verified against the dictionary.
SLICER_TYPE_CODES = frozenset({"CCS", "SLI", "TSX"})

# Type codes that are the machine line itself: the classic slicer codes plus
# the Textor slicer machines (TS500/TS700), whose type code is not CCS/SLI/TSX.
LINE_PART_TYPE_CODES = SLICER_TYPE_CODES | frozenset({"TS5", "TS7"})

# Component types the dictionary itself labels as the machine line or its
# accessories: "Line" = the Weber line material (WLN, MCS, SLC, ...),
# "Line Accessories" / "Multi Line Accessories" = the WLZ/TLZ/WAZ Zubehoer
# rows, "Slicer" = the slicer component itself (every CCS/SLI/TSX row carries
# it). Verified against the dictionary dump.
LINE_PART_COMPONENT_TYPES = frozenset(
    {"Line", "Line Accessories", "Multi Line Accessories", "Slicer"}
)

_ACCESSORY_RE = re.compile(r"\baccessor(?:y|ies)\b", re.IGNORECASE)

# Line accessories are named in English as "accessory ...", "accessories ..."
# or "accessories slicing line" (or the short "accessories"). Only this exact
# wording hides a material: every other number stays visible for a human.
_LINE_PART_NAME_RE = re.compile(r"\baccessor(?:y|ies)\b|slicing\s+line", re.IGNORECASE)


def _clean_text(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def _mentions_accessory(*values: str | None) -> bool:
    return any(_ACCESSORY_RE.search(value) for value in values if value)


def normalize_slicer_model(name_en: str | None, description: str | None = None) -> str | None:
    """Extract a pure Slicer product/model name without aggressive matching.

    Known variants are collapsed:

    * Slicer 405-Basic / Slicer 405-Extended -> Slicer 405
    * Slicer 604-1 / Slicer 604-2 -> Slicer 604
    * CCS 7000 E2 / CCS 7000 M6 / Slicer CCS 7000 -> Slicer 7000
    * Slicer weSLICE 4000 -> weSLICE 4000

    Any accessory wording rejects the candidate before matching. If both source
    fields contain conflicting model candidates, the English name wins.
    """
    primary = _clean_text(name_en)
    secondary = _clean_text(description)
    candidates = [value for value in (primary, secondary) if value]
    if not candidates:
        return None

    if _mentions_accessory(*candidates):
        return None

    def parse(value: str) -> str | None:
        match = re.search(
            r"\bwe\s*slice\s+((?:\d{3,4})(?:\s*/\s*\d{3,4})?|7\s*x\s*00)\b",
            value,
            flags=re.IGNORECASE,
        )
        if match:
            model = re.sub(r"\s+", "", match.group(1)).upper()
            return f"weSLICE {model}"

        # CCS is an explicit Slicer model family in this dictionary. Ignore
        # suffixes like E2/M6 after the numeric model.
        match = re.search(r"\bCCS\s*([0-9]{3,4})\b", value, flags=re.IGNORECASE)
        if match:
            return f"Slicer {match.group(1)}"

        match = re.search(
            r"\b(?:computer\s*-?\s*slicer|slicer)\s+(?:CCS\s+)?([0-9]{3,4})"
            r"(?:\s*[-–]\s*(?:basic|extended|[12]))?\b",
            value,
            flags=re.IGNORECASE,
        )
        if match:
            return f"Slicer {match.group(1)}"

        match = re.search(r"\bTextor\s+TS\s*([0-9]{3})\s+Slicer\b", value, flags=re.IGNORECASE)
        if match:
            return f"Textor Slicer TS{match.group(1)}"

        if re.search(r"\bTextor\s+Slicer\b", value, flags=re.IGNORECASE):
            return "Textor Slicer"
        return None

    for candidate in candidates:
        model = parse(candidate)
        if model is not None:
            return model
    return None


def slicer_model_from_material(material_no: str | None) -> str | None:
    """Extract a slicer model from a material number, without guessing.

    Only the CCS formats observed in the real dictionary are handled:

        CCS 302-376   -> Slicer 302   (model then serial)
        CCS04051      -> Slicer 405   (CCS0<model><sequence>)

    Any other format returns None so the caller flags the row for a human.
    """
    value = _clean_text(material_no)
    if not value:
        return None
    match = re.search(r"\bCCS\s+(\d{3})(?:\D|$)", value, re.IGNORECASE)
    if match:
        return f"Slicer {match.group(1)}"
    match = re.search(r"\bCCS0(\d{3})\d\b", value, re.IGNORECASE)
    if match:
        return f"Slicer {match.group(1)}"
    return None


def slicer_model_for(
    type_code: str | None,
    name_en: str | None,
    description: str | None,
    material_no: str | None,
) -> str | None:
    """Resolve the slicer model of a component, or None when it cannot be known.

    The English name is authoritative. Only when it names no model and is not
    an accessory is the material number consulted. Accessory rows stay
    unresolved on purpose: they must never be guessed into a nearby slicer.
    """
    if (type_code or "").strip().upper() not in SLICER_TYPE_CODES:
        return None
    model = normalize_slicer_model(name_en, description)
    if model is not None:
        return model
    if _mentions_accessory(name_en, description):
        return None
    return slicer_model_from_material(material_no)


def is_line_part(
    type_code: str | None,
    component_type: str | None,
    name_en: str | None,
) -> bool:
    """True when the dictionary says this material is part of the machine line.

    Line parts are priced through the family hours of the machine's line row
    (equipment_catalog, keyed by machine_type). Pricing them again as a module
    would charge the same machine twice, and the family cannot come from the
    material: the same accessory (e.g. WLZ03051) is installed on machines of
    family 30x and of family 1000, so the machine decides the family, never
    the material.

    Four clauses, each verified against the dictionary dump: the type code is
    a slicer/Textor code, the component type is a line family, the English
    name carries accessory or slicing-line wording. Anything else stays
    unresolved so a human classifies it (810 Röntgenscanner setup, 904 spare
    parts package, the CFV folding devices).

    This classifies only the material itself. An explicit workload rule always
    wins: callers check the rule first, so a linked material with hours is
    priced by its rule even if it looks like a line part, and a linked rule
    without hours keeps the material visible as pending hours.
    """
    if (type_code or "").strip().upper() in LINE_PART_TYPE_CODES:
        return True
    if (component_type or "").strip() in LINE_PART_COMPONENT_TYPES:
        return True
    return _LINE_PART_NAME_RE.search(name_en or "") is not None
