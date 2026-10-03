from fastapi import APIRouter, Request

from app.core.templates import templates


router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/home.html",
        context={},
    )


@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/about.html",
        context={
            "version": "0.1.0",
        },
    )