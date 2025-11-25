from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.rate_limiter import rate_limiter
from app.routes.routes import router as api_router
import sentry_sdk

sentry_sdk.init(
    dsn="https://4b29bcbfa434d4cce839f28c884e2309@o4510356941897728.ingest.us.sentry.io/4510356943470592",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


app = FastAPI(
    title="Experian POC API",
    version="1.0.0",
)

origins = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(rate_limiter)

app.include_router(api_router, prefix="/api/poc")
