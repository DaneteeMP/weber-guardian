"""Component name dictionary HTTP. Thin: validates, calls the service, maps errors.

The dictionary is global reference data, not per-filial, so these endpoints do
not take a subsidiary scope: every filial resolves the same names. Only
editing is restricted, because a wrong name changes what every filial sees.
"""
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.component_names import service
from app.modules.component_names.schemas import (
    ComponentNameOut,
    ComponentNameUpdateIn,
    ImportReportOut,
)

router = APIRouter(prefix="/component-names", tags=["component-names"])


@router.post("/import", response_model=ImportReportOut)
async def import_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    """Clean an uploaded names_dictionary.csv and replace the dictionary.

    The report is the point of the endpoint: a dirty file must show what was
    dropped and what still needs a decision, not silently replace the table.
    """
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="uploaded file is empty",
        )
    try:
        return service.import_dictionary(db, content)
    except service.DictionaryFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("", response_model=list[ComponentNameOut])
def list_endpoint(
    response: Response,
    search: str | None = Query(default=None, min_length=1, max_length=128),
    component_type: str | None = Query(default=None, min_length=1, max_length=128),
    only_conflicts: bool = Query(default=False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    rows = service.list_component_names(
        db,
        search=search,
        component_type=component_type,
        only_conflicts=only_conflicts,
        limit=limit,
        offset=offset,
    )
    response.headers["X-Total-Count"] = str(
        service.count_component_names(
            db, search=search, component_type=component_type, only_conflicts=only_conflicts
        )
    )
    return rows


@router.get("/export")
def export_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Download the cleaned dictionary as the same five-column CSV.

    cp1252 and semicolons on purpose: that is what the legacy file uses, so the
    download opens in Excel and can be imported again unchanged.
    """
    text = service.export_component_names(db)
    return Response(
        content=text.encode("cp1252", errors="replace"),
        media_type="text/csv; charset=cp1252",
        headers={"Content-Disposition": 'attachment; filename="names_dictionary_clean.csv"'},
    )


@router.patch("/{material_no}", response_model=ComponentNameOut)
def update_endpoint(
    material_no: str,
    payload: ComponentNameUpdateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    """Settle a conflicting entry by hand."""
    try:
        return service.update_component_name(
            db, material_no, payload.model_dump(exclude_none=True)
        )
    except service.ComponentNameNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component name not found: {material_no}",
        ) from exc
