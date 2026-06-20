from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devlens.db.base import Base
from devlens.db.session import engine
from devlens.routers import costs, insights, models, overview, projects, sessions, sync, tools


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="DevLens API",
        description="AI-Assisted Development Analytics Platform",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = "/api"
    app.include_router(sync.router, prefix=prefix)
    app.include_router(overview.router, prefix=prefix)
    app.include_router(projects.router, prefix=prefix)
    app.include_router(sessions.router, prefix=prefix)
    app.include_router(tools.router, prefix=prefix)
    app.include_router(costs.router, prefix=prefix)
    app.include_router(insights.router, prefix=prefix)
    app.include_router(models.router, prefix=prefix)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
