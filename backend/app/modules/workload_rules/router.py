"""HTTP API for global workload rules, material links and resolution checks.

Literal paths (/materials/..., /unresolved) are declared before /{rule_id} so
they are never parsed as a rule id.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.workload_rules import service
from app.modules.workload_rules.models import RULE_CATEGORIES
from app.modules.workload_rules.schemas import (
    MaterialLinkIn,
    MaterialLinkOut,
    MaterialResolutionOut,
    MaterialRuleOut,
    RuleMaterialOut,
    UnresolvedMaterialOut,
    WorkloadRuleCreateIn,
    WorkloadRuleDetailOut,
    WorkloadRuleOut,
    WorkloadRuleUpdateIn,
)

router = APIRouter(prefix="/workload-rules", tags=["workload-rules"])

WRITE_ROLES = require_role("admin", "sales")


def _rule_out(rule, linked: int) -> WorkloadRuleOut:
    return WorkloadRuleOut(
        id=rule.id,
        name=rule.name,
        workload=rule.workload,
        legacy_type_code=rule.legacy_type_code,
        category=rule.category,
        needs_review=rule.needs_review,
        note=rule.note,
        linked_materials=linked,
        created_at=rule.created_at,
    )


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


@router.get("", response_model=list[WorkloadRuleOut])
def list_rules_endpoint(
    response: Response,
    search: str | None = Query(default=None, min_length=1, max_length=128),
    needs_review: bool | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    if category is not None and category not in RULE_CATEGORIES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="unknown category")
    rows = service.list_rules(db, search=search, needs_review=needs_review, category=category, limit=limit, offset=offset)
    response.headers["X-Total-Count"] = str(
        service.count_rules(db, search=search, needs_review=needs_review, category=category)
    )
    return [_rule_out(rule, linked) for rule, linked in rows]


@router.post("", response_model=WorkloadRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule_endpoint(
    payload: WorkloadRuleCreateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    try:
        rule = service.create_rule(db, payload)
    except service.WorkloadRuleNameTaken as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="a workload rule with this name already exists") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return _rule_out(rule, 0)


@router.get("/materials/resolve", response_model=MaterialResolutionOut)
def resolve_material_endpoint(
    material_no: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Explain how a material number (e.g. CCW01001 or CCW01001-10901) resolves."""
    result = service.resolve_material(db, material_no)
    rule = None
    if result.rule is not None:
        rule = MaterialRuleOut(
            id=result.rule.id,
            name=result.rule.name,
            workload=result.rule.workload,
            needs_review=result.rule.needs_review,
        )
    return MaterialResolutionOut(
        material_no=result.material_no,
        state=result.state,
        dictionary_material_no=result.dictionary_material_no,
        name_en=result.name_en,
        type_code=result.type_code,
        component_type=result.component_type,
        has_conflict=result.has_conflict,
        rule=rule,
        customers=result.customers,
    )


@router.get("/unresolved", response_model=list[UnresolvedMaterialOut])
def unresolved_endpoint(
    response: Response,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Installed materials that are not priced, or need a human decision."""
    rows = service.unresolved_materials(db)
    response.headers["X-Total-Count"] = str(len(rows))
    return [
        UnresolvedMaterialOut(
            material_no=row.material_no,
            name_en=row.name_en,
            type_code=row.type_code,
            component_type=row.component_type,
            reason=row.reason,
            customers=row.customers,
        )
        for row in service.paginate(rows, limit, offset)
    ]


@router.put("/materials/{material_no}", response_model=MaterialLinkOut)
def link_material_endpoint(
    material_no: str,
    payload: MaterialLinkIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    """Link a material to a rule. If it already has another rule, it is moved."""
    try:
        result = service.link_material(db, material_no, payload.workload_rule_id)
    except service.WorkloadRuleNotFound as exc:
        raise _not_found("workload rule not found") from exc
    except service.MaterialNotFound as exc:
        raise _not_found("material is not in the component dictionary") from exc
    except service.MaterialLinkConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="material was linked concurrently, retry") from exc
    return MaterialLinkOut(
        material_no=result.material_no,
        workload_rule_id=result.workload_rule_id,
        previous_rule_id=result.previous_rule_id,
        previous_rule_name=result.previous_rule_name,
        changed=result.changed,
    )


@router.delete("/materials/{material_no}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_material_endpoint(
    material_no: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    if not service.unlink_material(db, material_no):
        raise _not_found("material is not linked to a workload rule")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{rule_id}", response_model=WorkloadRuleDetailOut)
def get_rule_endpoint(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    try:
        rule = service.get_rule(db, rule_id)
    except service.WorkloadRuleNotFound as exc:
        raise _not_found("workload rule not found") from exc
    materials = service.rule_materials(db, rule_id)
    base = _rule_out(rule, len(materials))
    return WorkloadRuleDetailOut(
        **base.model_dump(),
        materials=[
            RuleMaterialOut(
                material_no=row.material_no,
                name_en=row.name_en,
                type_code=row.type_code,
                component_type=row.component_type,
                has_conflict=row.has_conflict,
                customers=row.customers,
            )
            for row in materials
        ],
    )


@router.patch("/{rule_id}", response_model=WorkloadRuleOut)
def update_rule_endpoint(
    rule_id: uuid.UUID,
    payload: WorkloadRuleUpdateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    """Change name, hours or review flag. Global: affects every future draft."""
    changes = payload.model_dump(exclude_unset=True)
    try:
        rule = service.update_rule(db, rule_id, changes)
    except service.WorkloadRuleNotFound as exc:
        raise _not_found("workload rule not found") from exc
    except service.WorkloadRuleNameTaken as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="a workload rule with this name already exists") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return _rule_out(rule, service.linked_count(db, rule.id))


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule_endpoint(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    """Delete a workload that no customer uses; 409 while materials are installed."""
    try:
        service.delete_rule(db, rule_id)
    except service.WorkloadRuleNotFound as exc:
        raise _not_found("workload rule not found") from exc
    except service.WorkloadRuleInUse as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
