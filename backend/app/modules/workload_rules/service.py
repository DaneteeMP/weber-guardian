"""Business operations on global workload rules and material links.

Resolution used everywhere (offers, the catalog search, the unresolved list):

    equipment.material_no
        -> component_names (dictionary row, normalized key)
        -> workload_rule_materials.material_no (exactly one rule, or none)
        -> workload_rules (the global hours)

A material with no link is never priced: it is reported as needing review.
Every write runs in one transaction; a failed write is rolled back explicitly
and never leaves a half-moved material behind.
"""
from dataclasses import dataclass, field
from decimal import Decimal
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.component_names.models import ComponentName
from app.modules.component_names.service import legacy_base_material_no, normalize_material_no
from app.modules.component_names.slicers import SLICER_TYPE_CODES, is_line_part
from app.modules.equipment.models import Equipment
from app.modules.workload_rules.models import (
    CATEGORY_MANUAL,
    WorkloadRule,
    WorkloadRuleMaterial,
)
from app.modules.workload_rules.schemas import WorkloadRuleCreateIn

# Keep IN (...) lists small enough for every database driver.
_CHUNK = 500


class WorkloadRuleNotFound(LookupError):
    """No workload rule exists for the requested id."""


class WorkloadRuleNameTaken(Exception):
    """Another rule already uses this name."""


class MaterialNotFound(LookupError):
    """The material number is not in the component dictionary."""


class MaterialLinkConflict(Exception):
    """The material was linked by a concurrent request while this one ran."""


class WorkloadRuleInUse(Exception):
    """Materials of the rule are installed at real customers; it cannot be deleted."""

    def __init__(self, customers: int) -> None:
        self.customers = customers
        super().__init__(
            f"{customers} customer(s) still have materials of this workload installed"
        )


@dataclass(frozen=True)
class MaterialLinkResult:
    material_no: str
    workload_rule_id: uuid.UUID
    previous_rule_id: uuid.UUID | None
    previous_rule_name: str | None
    changed: bool


@dataclass(frozen=True)
class MaterialRow:
    """One material of a rule, with its dictionary data."""

    material_no: str
    name_en: str | None
    type_code: str | None
    component_type: str | None
    has_conflict: bool
    customers: int


@dataclass(frozen=True)
class Resolution:
    """How one material number resolves today.

    state:
      * "resolved": dictionary row found and linked to a rule;
      * "no_rule": dictionary row found, not linked to any rule;
      * "not_in_dictionary": no dictionary row for this number;
      * "slicer": part of the machine line (slicer/Textor code, or a material
        the dictionary marks as a line part); priced by the family line row
        of its machine, never as a module.
    """

    material_no: str
    state: str
    dictionary_material_no: str | None
    name_en: str | None
    type_code: str | None
    component_type: str | None
    has_conflict: bool
    rule: WorkloadRule | None
    customers: int


@dataclass(frozen=True)
class UnresolvedRow:
    material_no: str
    name_en: str | None
    type_code: str | None
    component_type: str | None
    reason: str
    customers: int


@dataclass
class _InstalledIndex:
    """Which customers have which equipment materials installed.

    Built once per request from the equipment table:
    * ``by_raw``: raw equipment material_no -> customer ids;
    * ``by_dictionary_key``: dictionary key (normalized or legacy base) ->
      customer ids. Lets a dictionary material be counted in O(1).
    """

    by_raw: dict[str, set[str]] = field(default_factory=dict)
    by_dictionary_key: dict[str, set[str]] = field(default_factory=dict)

    def customers_for(self, dictionary_key: str) -> int:
        return len(self.by_dictionary_key.get(dictionary_key, set()))


def _clean(text: str | None) -> str:
    return " ".join((text or "").split()).strip()


def _review_state(workload: Decimal | None, needs_review: bool | None) -> bool:
    """Create-time rule: without hours a rule is always under review by default."""
    if needs_review is None:
        return workload is None
    if workload is None and needs_review is False:
        raise ValueError("a workload rule without hours must remain marked for review")
    return needs_review


def _rules_filtered(
    search: str | None,
    needs_review: bool | None,
    category: str | None,
):
    statement = select(WorkloadRule)
    if search:
        pattern = f"%{_clean(search)}%"
        statement = statement.where(
            WorkloadRule.name.ilike(pattern) | WorkloadRule.legacy_type_code.ilike(pattern)
        )
    if needs_review is not None:
        statement = statement.where(WorkloadRule.needs_review.is_(needs_review))
    if category:
        statement = statement.where(WorkloadRule.category == category)
    return statement


def list_rules(
    db: Session,
    search: str | None = None,
    needs_review: bool | None = None,
    category: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[tuple[WorkloadRule, int]]:
    """One page of rules, each with the number of materials linked to it."""
    rules = list(
        db.scalars(
            _rules_filtered(search, needs_review, category)
            .order_by(WorkloadRule.name)
            .limit(limit)
            .offset(offset)
        )
    )
    if not rules:
        return []
    counts = dict(
        db.execute(
            select(WorkloadRuleMaterial.workload_rule_id, func.count(WorkloadRuleMaterial.id))
            .where(WorkloadRuleMaterial.workload_rule_id.in_([rule.id for rule in rules]))
            .group_by(WorkloadRuleMaterial.workload_rule_id)
        ).all()
    )
    return [(rule, int(counts.get(rule.id, 0))) for rule in rules]


def count_rules(
    db: Session,
    search: str | None = None,
    needs_review: bool | None = None,
    category: str | None = None,
) -> int:
    statement = _rules_filtered(search, needs_review, category).with_only_columns(WorkloadRule.id)
    return db.scalar(select(func.count()).select_from(statement.subquery())) or 0


def get_rule(db: Session, rule_id: uuid.UUID) -> WorkloadRule:
    rule = db.get(WorkloadRule, rule_id)
    if rule is None:
        raise WorkloadRuleNotFound(str(rule_id))
    return rule


def create_rule(db: Session, data: WorkloadRuleCreateIn) -> WorkloadRule:
    name = _clean(data.name)
    rule = WorkloadRule(
        name=name,
        workload=data.workload,
        legacy_type_code=_clean(data.legacy_type_code) or None,
        category=CATEGORY_MANUAL,
        needs_review=_review_state(data.workload, data.needs_review),
        note=None,
    )
    db.add(rule)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise WorkloadRuleNameTaken(name) from None
    db.refresh(rule)
    return rule


def update_rule(db: Session, rule_id: uuid.UUID, changes: dict) -> WorkloadRule:
    """Edit the name, hours, legacy code and review flag of a global rule.

    ``changes`` only contains the fields the caller sent, so an omitted field
    keeps its stored value. The category is not editable. The legacy code is
    just a label, so any value is accepted and it is not unique.
    A change here is global: every future draft that resolves to this rule
    uses the new value.
    """
    rule = get_rule(db, rule_id)

    next_workload = changes["workload"] if "workload" in changes else rule.workload

    explicit_review = changes.get("needs_review")
    if explicit_review is not None:
        next_review = explicit_review
    elif next_workload is None:
        next_review = True
    else:
        # Keep the stored flag: e.g. a CONFLICT note stays flagged after a rename.
        next_review = rule.needs_review
    if next_workload is None and next_review is False:
        raise ValueError("a workload rule without hours must remain marked for review")

    if changes.get("name") is not None:
        rule.name = _clean(changes["name"])
    if "legacy_type_code" in changes:
        rule.legacy_type_code = _clean(changes["legacy_type_code"]) or None
    rule.workload = next_workload
    rule.needs_review = next_review
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise WorkloadRuleNameTaken(_clean(changes.get("name"))) from None
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: uuid.UUID) -> int:
    """Delete a workload nobody uses, dropping its material links with it.

    "In use" means a linked material is installed at a real customer: those
    machines price through this rule today, so it raises WorkloadRuleInUse
    (mapped to 409 by the router) and the editor must unlink the materials
    first. A rule whose materials are not installed anywhere is dead catalog
    data; deleting it removes the rule and its links in one transaction.

    Returns how many material links disappeared with the rule.
    """
    rule = get_rule(db, rule_id)
    linked = list(
        db.scalars(
            select(WorkloadRuleMaterial.material_no).where(
                WorkloadRuleMaterial.workload_rule_id == rule.id
            )
        )
    )
    installed = _installed_index(db)
    customers: set[str] = set()
    for material_no in linked:
        customers |= installed.by_dictionary_key.get(material_no, set())
    if customers:
        raise WorkloadRuleInUse(len(customers))

    db.delete(rule)
    db.commit()
    return len(linked)


def _installed_index(db: Session) -> _InstalledIndex:
    """Build the installed-material index from the equipment table in one query."""
    index = _InstalledIndex()
    pairs = db.execute(
        select(Equipment.customer_id, Equipment.material_no)
        .where(Equipment.material_no.is_not(None))
        .distinct()
    ).all()
    for customer_id, raw in pairs:
        index.by_raw.setdefault(raw, set()).add(customer_id)
        for key in {normalize_material_no(raw), legacy_base_material_no(raw)}:
            index.by_dictionary_key.setdefault(key, set()).add(customer_id)
    return index


def _names_for_keys(db: Session, keys: set[str]) -> dict[str, ComponentName]:
    found: dict[str, ComponentName] = {}
    ordered = sorted(keys)
    for start in range(0, len(ordered), _CHUNK):
        chunk = ordered[start : start + _CHUNK]
        for name in db.scalars(select(ComponentName).where(ComponentName.material_no.in_(chunk))):
            found[name.material_no] = name
    return found


def _dictionary_name(names: dict[str, ComponentName], raw: str) -> ComponentName | None:
    """Same lookup order as the maintenance draft: model-aware key, then legacy base."""
    return names.get(normalize_material_no(raw)) or names.get(legacy_base_material_no(raw))


def rules_by_material(db: Session, material_nos: set[str]) -> dict[str, WorkloadRule]:
    """Dictionary material_no -> the rule it is linked to (materials without a rule are absent)."""
    found: dict[str, WorkloadRule] = {}
    ordered = sorted(material_nos)
    for start in range(0, len(ordered), _CHUNK):
        chunk = ordered[start : start + _CHUNK]
        rows = db.execute(
            select(WorkloadRuleMaterial.material_no, WorkloadRule)
            .join(WorkloadRule, WorkloadRule.id == WorkloadRuleMaterial.workload_rule_id)
            .where(WorkloadRuleMaterial.material_no.in_(chunk))
        ).all()
        for material_no, rule in rows:
            found[material_no] = rule
    return found


def linked_count(db: Session, rule_id: uuid.UUID) -> int:
    """How many materials point at this rule (no customer counting)."""
    return int(
        db.scalar(
            select(func.count(WorkloadRuleMaterial.id)).where(
                WorkloadRuleMaterial.workload_rule_id == rule_id
            )
        )
        or 0
    )


def rule_materials(db: Session, rule_id: uuid.UUID) -> list[MaterialRow]:
    """Materials linked to one rule, with dictionary data and customer counts."""
    get_rule(db, rule_id)
    linked = list(
        db.scalars(
            select(WorkloadRuleMaterial.material_no)
            .where(WorkloadRuleMaterial.workload_rule_id == rule_id)
            .order_by(WorkloadRuleMaterial.material_no)
        )
    )
    names = _names_for_keys(db, set(linked))
    installed = _installed_index(db)

    rows: list[MaterialRow] = []
    for material_no in linked:
        name = names.get(material_no)
        rows.append(
            MaterialRow(
                material_no=material_no,
                name_en=name.name_en if name else None,
                type_code=name.type_code if name else None,
                component_type=name.component_type if name else None,
                has_conflict=bool(name.has_conflict) if name else False,
                customers=installed.customers_for(material_no),
            )
        )
    return rows


def link_material(db: Session, material_no: str, rule_id: uuid.UUID) -> MaterialLinkResult:
    """Attach a material to a rule, moving it when it already has another rule.

    A move is one UPDATE of the existing link row, so the material never
    belongs to two rules and never to none in between.
    """
    material = _clean(material_no)
    rule = get_rule(db, rule_id)

    dictionary_row = db.scalar(select(ComponentName.id).where(ComponentName.material_no == material))
    if dictionary_row is None:
        raise MaterialNotFound(material)

    existing = db.scalar(
        select(WorkloadRuleMaterial).where(WorkloadRuleMaterial.material_no == material)
    )
    if existing is not None and existing.workload_rule_id == rule.id:
        return MaterialLinkResult(material, rule.id, rule.id, rule.name, changed=False)

    previous_id = existing.workload_rule_id if existing is not None else None
    previous_name = None
    if previous_id is not None:
        previous_name = db.scalar(select(WorkloadRule.name).where(WorkloadRule.id == previous_id))

    if existing is None:
        db.add(WorkloadRuleMaterial(workload_rule_id=rule.id, material_no=material))
    else:
        existing.workload_rule_id = rule.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise MaterialLinkConflict(material) from None
    return MaterialLinkResult(material, rule.id, previous_id, previous_name, changed=True)


def unlink_material(db: Session, material_no: str) -> bool:
    """Detach a material from its rule. Returns False when it had no rule."""
    material = _clean(material_no)
    existing = db.scalar(
        select(WorkloadRuleMaterial).where(WorkloadRuleMaterial.material_no == material)
    )
    if existing is None:
        return False
    db.delete(existing)
    db.commit()
    return True


def resolve_material(db: Session, material_no: str) -> Resolution:
    """Explain how one material number (raw or normalized) resolves today."""
    raw = _clean(material_no)
    names = _names_for_keys(db, {raw, normalize_material_no(raw), legacy_base_material_no(raw)})
    name = names.get(raw) or _dictionary_name(names, raw)
    installed = _installed_index(db)

    if name is None:
        return Resolution(
            raw, "not_in_dictionary", None, None, None, None, False, None,
            len(installed.by_raw.get(raw, set())),
        )

    if (name.type_code or "").strip().upper() in SLICER_TYPE_CODES:
        # The machine is the line: no rule can turn a slicer code into a module.
        return Resolution(
            raw, "slicer", name.material_no, name.name_en, name.type_code,
            name.component_type, bool(name.has_conflict), None,
            installed.customers_for(name.material_no),
        )

    # An explicit rule wins over the classifier: a linked material is priced
    # by its rule (or, with rule.workload = None, waits for hours).
    rule = rules_by_material(db, {name.material_no}).get(name.material_no)
    if rule is None and is_line_part(name.type_code, name.component_type, name.name_en):
        state = "slicer"
    else:
        state = "resolved" if rule is not None else "no_rule"
    return Resolution(
        raw,
        state,
        name.material_no,
        name.name_en,
        name.type_code,
        name.component_type,
        bool(name.has_conflict),
        rule,
        installed.customers_for(name.material_no),
    )


def unresolved_materials(db: Session) -> list[UnresolvedRow]:
    """Installed materials that cannot be priced, or that need a human decision.

    Reasons:
      * no_rule: installed, known in the dictionary, not linked to any rule;
      * no_hours: linked to a rule that has no workload yet (pending hours);
      * dictionary_conflict: the dictionary holds conflicting values for it;
      * not_in_dictionary: installed, but the dictionary has no row for it.

    The machine line itself never appears: slicer type codes are excluded
    outright, and so is every material the dictionary marks as a line part
    (is_line_part), because the family line row of the machine prices those.
    Two decisions keep a row visible anyway: a dictionary conflict always
    needs a human, and an explicit rule wins over the classifier, so a linked
    material shows as no_hours while its rule has no workload.
    """
    installed = _installed_index(db)
    candidate_keys: set[str] = set()
    for raw in installed.by_raw:
        candidate_keys.add(normalize_material_no(raw))
        candidate_keys.add(legacy_base_material_no(raw))
    names = _names_for_keys(db, candidate_keys)

    dictionary_keys: set[str] = set()
    missing: dict[str, set[str]] = {}
    for raw, owners in installed.by_raw.items():
        name = _dictionary_name(names, raw)
        if name is None:
            missing.setdefault(normalize_material_no(raw), set()).update(owners)
        else:
            dictionary_keys.add(name.material_no)

    rules = rules_by_material(db, dictionary_keys)
    rows: list[UnresolvedRow] = []

    for dictionary_key in sorted(dictionary_keys):
        name = names[dictionary_key]
        if (name.type_code or "").strip().upper() in SLICER_TYPE_CODES:
            continue
        if name.has_conflict:
            reason = "dictionary_conflict"
        elif dictionary_key not in rules:
            if is_line_part(name.type_code, name.component_type, name.name_en):
                continue  # priced by the family line row of its machine
            reason = "no_rule"
        elif rules[dictionary_key].workload is None:
            reason = "no_hours"
        else:
            continue
        rows.append(
            UnresolvedRow(
                dictionary_key,
                name.name_en,
                name.type_code,
                name.component_type,
                reason,
                installed.customers_for(dictionary_key),
            )
        )

    for key, owners in missing.items():
        rows.append(UnresolvedRow(key, None, None, None, "not_in_dictionary", len(owners)))

    return sorted(rows, key=lambda row: (row.reason, row.material_no))


def paginate(rows: list, limit: int, offset: int) -> list:
    """Slice a computed list. The total is always the length of the full list."""
    return rows[offset : offset + limit]
