from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.persistence.models import Base
from infrastructure.persistence.schema_patches import ensure_schema_patches
from infrastructure.seed import seed_database
from interfaces.routers import auth, bot, buildings, specialists, tickets, triage


@asynccontextmanager
async def lifespan(app: FastAPI):
    import interfaces.deps as deps

    Base.metadata.create_all(bind=deps._engine)
    ensure_schema_patches(deps._engine)
    session = deps.SessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()
    yield


app = FastAPI(title="Smart City MVP Ticket System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(buildings.router)
app.include_router(triage.router)
app.include_router(tickets.router)
app.include_router(specialists.router)
app.include_router(bot.router)


@app.get("/health")
def health():
    return {"status": "ok"}
