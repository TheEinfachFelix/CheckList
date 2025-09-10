from typing import Union

from fastapi import APIRouter, FastAPI
from router.RouteTaskItems import router

app = FastAPI()

app.include_router(router)
