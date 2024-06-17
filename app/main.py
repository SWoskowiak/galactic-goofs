import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from routers import spacecraft
from services.spacecraft import set_random_spacecraft_to_malfunction
from config import config
from services.spacecraft import SpacecraftStatus
from services.db import db_session
from services.event import PubSub, EVENTS as spacecraft_events


# Have fastapi lifespan system handle the malfunction startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodically_set_spacecraft_to_malfunction())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

app.include_router(spacecraft.router, prefix="/spacecraft", tags=["spacecraft"])
templates = Jinja2Templates(directory=config.TEMPLATES_DIRECTORY)


# LANDING PAGE ##################################################################################
@app.get("/")
async def read_index(request: Request):
    """Base landing page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "SpacecraftStatus": SpacecraftStatus},
    )


# RANDOM MALFUNCTION LOOP #######################################################################
async def periodically_set_spacecraft_to_malfunction():
    async with db_session() as db:
        """Every 5 seconds, randomly select a spacecraft and set its status to 'MALFUNCTION'"""
        try:
            while True:
                causedMalfunction = await set_random_spacecraft_to_malfunction(db)
                if causedMalfunction:
                    await db.commit()  # Commit the malfunction
                    PubSub.publish(
                        spacecraft_events.RANDOM_MALFUNCTION
                    )  # Let connected clients know the malfunction occured
                await asyncio.sleep(5)  # Wait 5 seconds
        except Exception as e:
            await db.rollback()  # Rollback on error
            raise e
