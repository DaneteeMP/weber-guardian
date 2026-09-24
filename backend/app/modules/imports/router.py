"""Import HTTP. Thin: reads the file bytes, calls the service, maps the report."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, require_role
from app.core.subsidiaries import normalize_subsidiary
from app.modules.imports import service
from app.modules.imports.schemas import ImportReport

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/upload", response_model=ImportReport)
async def upload_endpoint(
    file: UploadFile,
    dry_run: bool = Query(default=True),
    subsidiary_id: str | None = Query(default=None, min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    # Real runs must tag every row: untagged data would be invisible to all
    # filials (only global users see NULL). Simulations may skip it.
    if not dry_run and not (subsidiary_id or "").strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="subsidiary_id is required for real imports",
        )
    # Scoped users import for their own filial only.
    if (
        current.subsidiary_id is not None
        and subsidiary_id
        and normalize_subsidiary(subsidiary_id) != current.subsidiary_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    content = await file.read()
    report = service.run_import(db, content, subsidiary_id=subsidiary_id, dry_run=dry_run)
    if report.errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=report.model_dump())
    return report
