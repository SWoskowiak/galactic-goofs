"""Spacecraft Service for CRUD operations and more"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
import random


class SpacecraftStatus:
    NONE = "NONE"
    NOMINAL = "NOMINAL"
    MALFUNCTIONING = "MALFUNCTIONING"


# Create a spacecraft
async def create_spacecraft(
    db: AsyncSession, name: str, cosparID: str, status: str
) -> bool:
    """Create a spacecraft"""
    query = text(
        "INSERT INTO spacecraft (name, cospar_id, status) VALUES (:name, :cosparID, :status) RETURNING *"
    )
    result = await db.execute(
        query, {"name": name, "cosparID": cosparID, "status": status}
    )
    return result.rowcount == 1


# Fetch "all" spacecraft
async def get_all_spacecraft(db: AsyncSession):
    """Fetch all spacecraft (with a safe limit for now)"""
    result = await db.execute(
        text("SELECT * FROM spacecraft ORDER BY id DESC LIMIT 500")
    )
    return result.all()


# Fetch a spacecraft by uuid
async def get_spacecraft_by_uuid(db: AsyncSession, spacecraft_uuid: str):
    """Fetch spacecraft by uuid"""
    result = await db.execute(
        text("SELECT * FROM spacecraft WHERE uuid = :uuid"),
        {"uuid": spacecraft_uuid},
    )
    return result.one()


# Delete a spacecraft by uuid
async def delete_spacecraft_by_uuid(db: AsyncSession, spacecraft_uuid: UUID) -> bool:
    """Delete a spacecraft by uuid"""
    query = text("DELETE FROM spacecraft WHERE uuid = :uuid")
    result = await db.execute(query, {"uuid": spacecraft_uuid})
    return result.rowcount == 1  # 1 == Deleted, 0 == Not deleted


async def set_random_spacecraft_to_malfunction(db: AsyncSession) -> bool:
    """Randomly select a spacecraft and set its status to 'MALFUNCTION'"""
    # Get all functioning spacecraft
    result = await db.execute(
        text("SELECT * from spacecraft WHERE status = :status"),
        {"status": SpacecraftStatus.NOMINAL},
    )

    # Randomly select a functional spacecraft if we have any
    functionalSpacecraft = result.all()
    if functionalSpacecraft:
        spacecraft = random.choice(functionalSpacecraft)
        # Set it to malfunction
        await set_spacecraft_status(
            db, spacecraft.uuid, SpacecraftStatus.MALFUNCTIONING
        )
        return True
        # No functional spacecraft to malfunction
    else:
        return False


# Set the status of a spacecraft and return the updated version
async def set_spacecraft_status(
    db: AsyncSession, spacecraft_uuid: UUID, status: str
) -> bool:
    """Update the status of a given spacecraft"""
    query = text("UPDATE spacecraft SET status = :status WHERE uuid = :uuid")
    print(f"SET STATUS TO: {status}")
    result = await db.execute(query, {"uuid": spacecraft_uuid, "status": status})
    print(f"ROWS UPDATED: {result.rowcount}")
    if result.rowcount == 0:
        raise ValueError(f"No spacecraft found with uuid '{spacecraft_uuid}'")

    return result.rowcount == 1
