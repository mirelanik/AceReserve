"""Court management API endpoints.
Handles court CRUD operations and availability queries.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from ..models.court import CourtCreate, CourtRead
from ..models.user import User
from ..auth.dependencies import require_admin
from ..core.dependencies_services import get_court_service
from ..services.court_service import CourtService

router = APIRouter(prefix="/courts", tags=["Courts"])


@router.post("/", response_model=CourtRead, status_code=201)
async def add_court(
    court_input: CourtCreate,
    current_user: User = Depends(require_admin),
    service: CourtService = Depends(get_court_service),
):
    return await service.create_court(court_input, current_user)


@router.delete("/{court_number}", status_code=200)
async def delete_court(
    court_number: int,
    current_user: User = Depends(require_admin),
    service: CourtService = Depends(get_court_service),
):
    return await service.remove_court(court_number, current_user)


@router.get("/all", response_model=list[CourtRead], status_code=200)
async def get_all_courts(service: CourtService = Depends(get_court_service)):
    return await service.show_all_courts()


@router.get("/{court_number}", response_model=CourtRead, status_code=200)
async def get_current_court(
    court_number: int, service: CourtService = Depends(get_court_service)
):
    return await service.show_court_by_number(court_number)


@router.get("/", response_model=list[CourtRead], status_code=200)
async def get_courts_by_category(
    surface: str | None = Query(None, description="Search by surface"),
    lighting: bool | None = Query(None, description="Search by lighting"),
    start_datetime: datetime | None = Query(
        None, description="Search by date and time (YYYY-MM-DDTHH:MM:SS)"
    ),
    service: CourtService = Depends(get_court_service),
):
    return await service.select_courts_by_category(
        surface, lighting, start_datetime=start_datetime
    )
