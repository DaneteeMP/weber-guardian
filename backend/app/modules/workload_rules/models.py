"""Global module workload rules and the dictionary materials linked to them.

Two tables, two responsibilities:

* ``workload_rules``: the real maintenance rule ("Checkweigher 100" = 1.00 h).
  One row per rule. ``legacy_type_code`` is traceability only; it is NOT unique
  because several rules came from the same legacy code (CCW, CCA, WPR).
* ``workload_rule_materials``: which dictionary material (``component_names``)
  uses which rule. ``material_no`` is UNIQUE, so one material has at most one
  rule. Moving a material is an update of this row, never a second row.

Workloads are global: there is no per-customer or per-machine override. A rule
change applies to every future maintenance draft that resolves to that rule.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# Where the rule came from. Kept as data so the UI and the audit can tell apart
# the reconstructed legacy TblWorkLoad rules from values carried over from the
# previous module table and rules created by hand.
CATEGORY_LEGACY = "legacy"
CATEGORY_CARRIED_OVER = "carried_over"
CATEGORY_MANUAL = "manual"
RULE_CATEGORIES = (CATEGORY_LEGACY, CATEGORY_CARRIED_OVER, CATEGORY_MANUAL)


class WorkloadRule(Base):
    """One global maintenance rule with its standard hours."""

    __tablename__ = "workload_rules"
    __table_args__ = (
        UniqueConstraint("name", name="uq_workload_rules_name"),
        CheckConstraint("workload IS NULL OR workload >= 0", name="ck_workload_rules_workload_nonnegative"),
        CheckConstraint(
            "category IN ('legacy', 'carried_over', 'manual')",
            name="ck_workload_rules_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # The real rule name, e.g. "Checkweigher 200 mono". Never a generic
    # category such as "Checkweigher".
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # Standard hours. NULL means "not configured yet" and always needs review.
    workload: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    # Legacy TblWorkLoad key (type_code). Traceability only, never an identity.
    legacy_type_code: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False, default=CATEGORY_LEGACY)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Why the rule needs review or what was decided, e.g. a conflicting legacy
    # value that was deliberately not changed.
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WorkloadRuleMaterial(Base):
    """Link from one dictionary material to one workload rule."""

    __tablename__ = "workload_rule_materials"
    __table_args__ = (
        # The business rule: a material belongs to at most one rule.
        UniqueConstraint("material_no", name="uq_workload_rule_materials_material_no"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workload_rule_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("workload_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Matches component_names.material_no. Deliberately not a foreign key: a
    # dictionary re-import may remove stale entries and must not be blocked.
    # The service checks that the material exists before linking it.
    material_no: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
