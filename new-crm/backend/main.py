from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from route import router

app = FastAPI()

app.include_router(router)

# Serve static frontend from "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Optional: if you want frontend JS to call /api/*
# (Not strictly needed since they share domain now)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Include your API routes at /api/*
#app.include_router(router, prefix="/api")
