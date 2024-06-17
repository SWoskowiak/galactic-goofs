import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from config import config
from services import spacecraft as spacecraftService
from services.db import get_db_session
from services.event import (
    EVENTS as spacecraft_events,
    PubSub as pubSub,
    sse_events_handler,
)

router = APIRouter()
logger = logging.getLogger(__name__)

templates = Jinja2Templates(config.TEMPLATES_DIRECTORY)


# SPACE CRAFT SSE EVENT STREAM ###########################################################
# SSE event stream route
@router.get("/stream", response_class=Response)
async def stream_sse_data(request: Request):
    """Stream data to clients"""
    return StreamingResponse(
        sse_events_handler(request), media_type="text/event-stream"
    )


# CREATE SPACECRAFT ######################################################################
@router.post("/")
async def create_spacecraft(
    name: str = Form(...),
    cosparID: str = Form(...),
    spacecraftStatus: str = Form(..., alias="status"),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a single spacecraft"""
    try:
        wasCreated = await spacecraftService.create_spacecraft(
            db, name, cosparID, spacecraftStatus
        )
    except Exception as e:
        logger.error(f"Failed to create spacecraft: {e}")
        raise HTTPException(
            status_code=500, detail="Error occured trying to create spacecraft"
        )
    pubSub.publish(spacecraft_events.CREATE_SPACECRAFT)
    if wasCreated:
        return Response(status_code=status.HTTP_201_CREATED)  # Successful create
    else:
        return Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )  # Unsuccessful


# GET LIST OF SPACECRAFT ######################################################################
@router.get("/list/")
async def get_spacecraft(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Get the spacecraft list component"""
    try:
        spacecraft = await spacecraftService.get_all_spacecraft(db)
    except Exception as e:
        logger.error(f"Failed to fetch spacecraft: {e}")
        raise HTTPException(
            status_code=500, detail="Error occured trying to get all spacecraft"
        )
    # Return rendered list of spacecraft
    return templates.TemplateResponse(
        "spacecraftList.html",
        {
            "request": request,
            "spacecrafts": spacecraft,
        },
    )


# REPAIR SPACECRAFT ######################################################################
@router.patch("/repair/{uuid}/")
async def patch_spacecraft_status(
    request: Request,
    uuid: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Repair a spacecraft with the provided UUID"""
    try:
        wasRepaired = await spacecraftService.set_spacecraft_status(
            db, uuid, spacecraftService.SpacecraftStatus.NOMINAL
        )
    except Exception as e:
        logger.error(f"Failed to repair spacecraft: {e}")
        raise HTTPException(
            status_code=500, detail="Error occured trying to repair spacecraft"
        )
    # Send repair SSE event
    pubSub.publish(spacecraft_events.REPAIR_SPACECRAFT)
    if wasRepaired:
        return Response(status_code=status.HTTP_204_NO_CONTENT)  # Success in patching
    else:
        return Response(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# DELETE SPACECRAFT ######################################################################
@router.delete("/{uuid}/")
async def delete_spacecraft(uuid: UUID, db: AsyncSession = Depends(get_db_session)):
    """Get the spacecraft list component"""
    try:
        wasDeleted = await spacecraftService.delete_spacecraft_by_uuid(db, uuid)
    except Exception as e:
        logger.error(f"Failed to delete spacecraft: {e}")
        raise HTTPException(
            status_code=500, detail="Error occured trying to delete spacecraft"
        )
    pubSub.publish(spacecraft_events.DELETE_SPACECRAFT)
    if wasDeleted:
        return Response(status_code=status.HTTP_200_OK)  # Successful delete
    else:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND, detail="spacecraft not found"
        )  # No outright failure just no spacecraft was found with that ID
