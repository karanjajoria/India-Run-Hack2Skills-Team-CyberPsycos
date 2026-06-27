from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="TalentIQ API",
    description="Hybrid candidate ranking engine for recruiters",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    # Pre-load embedding model to avoid cold start on first request
    from app.services.embeddings import get_model
    from app.services.vector_store import ensure_collection
    try:
        get_model()
        ensure_collection()
        print("✅ Embedding model loaded | Qdrant collection ready")
    except Exception as e:
        print(f"⚠️  Startup warning: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
