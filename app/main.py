"""Entry point that wires the API routers and serves the static frontend."""
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers import upload, dashboard

# Loads variables from a local .env file, so ADMIN_TOKEN and the Turso
# variables do not need to be exported by hand during development.
load_dotenv()

app = FastAPI(title="HCMP Dashboard")

# Routers are included before the static mount below, so API paths are
# matched first and the catch all static mount only serves everything else.
app.include_router(upload.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    # Creates the database tables the first time the app runs.
    init_db()


# Serves index.html, admin.html and the js/css files as plain static assets.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
