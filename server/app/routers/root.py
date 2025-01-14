from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

import main

router = APIRouter(
    tags=["Root"]
)

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return main.templates.TemplateResponse("index.html", {"request": request})
