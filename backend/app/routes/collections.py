import logging

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.bezpeka.csrf import (
    CSRF_COOKIE_MAX_AGE,
    CSRF_COOKIE_NAME,
    generate_csrf_token,
    validate_csrf_token,
)
from app.bezpeka.sesii import (
    SESSION_COOKIE_NAME,
)
from app.core.templates import templates
from app.schemas.collection import (
    CollectionCreate,
)
from app.services.collection_service import (
    create_collection,
    get_user_collection,
    get_user_collections,
)
from app.services.document_service import (
    get_collection_documents,
    search_collection_documents,
)
from app.services.hybrid_search_service import (
    HYBRID_LEXICAL_WEIGHT,
    HYBRID_SEMANTIC_WEIGHT,
    search_hybrid_documents,
)
from app.services.semantic_search_service import (
    search_semantic_documents,
)
from app.services.session_service import (
    get_user_by_session_token,
)


router = APIRouter(
    tags=["collections"],
)

logger = logging.getLogger(__name__)

ALLOWED_SEARCH_MODES = {
    "lexical",
    "semantic",
    "hybrid",
}


def set_csrf_cookie(
    response,
    csrf_token: str,
):
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=CSRF_COOKIE_MAX_AGE,
        httponly=True,
        samesite="strict",
        secure=False,
        path="/",
    )

    return response


def get_current_user(
    request: Request,
    session: Session,
):
    session_token = request.cookies.get(
        SESSION_COOKIE_NAME
    )

    return get_user_by_session_token(
        session=session,
        session_token=session_token,
    )


def render_collections_page(
    request: Request,
    user,
    collections,
    csrf_token: str,
    errors: list[str] | None = None,
    form_data: dict[str, str] | None = None,
    status_code: int = 200,
):
    return templates.TemplateResponse(
        request=request,
        name="collections/index.html",
        context={
            "user": user,
            "collections": collections,
            "csrf_token": csrf_token,
            "errors": errors or [],
            "form_data": form_data or {},
        },
        status_code=status_code,
    )


@router.get("/collections")
def collections_page(
    request: Request,
    deleted: int | None = None,
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    collections = get_user_collections(
        session=session,
        user=user,
    )

    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    new_cookie_needed = False

    if csrf_token is None:
        csrf_token = generate_csrf_token()
        new_cookie_needed = True

    response = templates.TemplateResponse(
        request=request,
        name="collections/index.html",
        context={
            "user": user,
            "collections": collections,
            "csrf_token": csrf_token,
            "errors": [],
            "form_data": {},
            "collection_deleted": (
                deleted == 1
            ),
        },
    )

    if new_cookie_needed:
        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return response


@router.post("/collections")
def create_collection_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    cookie_csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    if not validate_csrf_token(
        form_token=csrf_token,
        cookie_token=cookie_csrf_token,
    ):
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    try:
        collection_data = CollectionCreate(
            name=name,
            description=description,
        )

    except ValidationError:
        collections = get_user_collections(
            session=session,
            user=user,
        )

        return render_collections_page(
            request=request,
            user=user,
            collections=collections,
            csrf_token=csrf_token,
            errors=[
                "Перевірте назву та опис колекції."
            ],
            form_data={
                "name": name,
                "description": description,
            },
            status_code=400,
        )

    try:
        create_collection(
            session=session,
            user=user,
            collection_data=collection_data,
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while creating collection."
        )

        collections = get_user_collections(
            session=session,
            user=user,
        )

        return render_collections_page(
            request=request,
            user=user,
            collections=collections,
            csrf_token=csrf_token,
            errors=[
                "Не вдалося створити колекцію."
            ],
            form_data={
                "name": name,
                "description": description,
            },
            status_code=500,
        )

    return RedirectResponse(
        url="/collections",
        status_code=303,
    )


@router.get(
    "/collections/{collection_id}"
)
def collection_detail_page(
    collection_id: int,
    request: Request,
    q: str = "",
    mode: str = "hybrid",
    upload_error: str | None = None,
    uploaded: int | None = None,
    updated: int | None = None,
    manage_error: str | None = None,
    session: Session = Depends(
        get_db_session
    ),
):
    user = get_current_user(
        request=request,
        session=session,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    collection = get_user_collection(
        session=session,
        user=user,
        collection_id=collection_id,
    )

    if collection is None:
        return RedirectResponse(
            url="/collections",
            status_code=303,
        )

    search_query = (
        " ".join(
            q.strip().split()
        )
    )[:200]

    search_mode = (
        mode.strip().lower()
    )

    if search_mode not in ALLOWED_SEARCH_MODES:
        search_mode = "hybrid"

    search_scores: dict[
        int,
        float,
    ] = {}

    score_label = ""

    if search_query:

        if search_mode == "lexical":
            search_results = (
                search_collection_documents(
                    session=session,
                    collection=collection,
                    search_text=search_query,
                )
            )

            score_label = "Lexical score"

        elif search_mode == "semantic":
            search_results = (
                search_semantic_documents(
                    session=session,
                    collection=collection,
                    search_text=search_query,
                    limit=50,
                )
            )

            score_label = (
                "Cosine similarity"
            )

        else:
            search_results = (
                search_hybrid_documents(
                    session=session,
                    collection=collection,
                    search_text=search_query,
                    lexical_weight=(
                        HYBRID_LEXICAL_WEIGHT
                    ),
                    semantic_weight=(
                        HYBRID_SEMANTIC_WEIGHT
                    ),
                    limit=50,
                )
            )

            score_label = "Hybrid score"

        documents = [
            result.document
            for result in search_results
        ]

        search_scores = {
            result.document.id:
                result.score
            for result in search_results
        }

    else:
        documents = get_collection_documents(
            session=session,
            collection=collection,
        )

    csrf_token = request.cookies.get(
        CSRF_COOKIE_NAME
    )

    new_cookie_needed = False

    if csrf_token is None:
        csrf_token = generate_csrf_token()
        new_cookie_needed = True

    errors: list[str] = []

    if upload_error == "too_large":
        errors.append(
            "Файл перевищує максимально "
            "дозволений розмір 10 МБ."
        )

    elif upload_error == "invalid":
        errors.append(
            "Некоректний файл. "
            "Дозволені PDF, DOCX та TXT."
        )

    elif upload_error == "csrf":
        errors.append(
            "Не вдалося перевірити "
            "безпечність запиту."
        )

    elif upload_error == "server":
        errors.append(
            "Не вдалося завантажити файл."
        )

    if manage_error == "validation":
        errors.append(
            "Перевірте назву та опис колекції."
        )

    elif manage_error == "csrf":
        errors.append(
            "Не вдалося перевірити "
            "безпечність запиту."
        )

    elif manage_error == "server":
        errors.append(
            "Не вдалося виконати операцію "
            "з колекцією."
        )

    response = templates.TemplateResponse(
        request=request,
        name="collections/detail.html",
        context={
            "user": user,
            "collection": collection,
            "documents": documents,
            "csrf_token": csrf_token,
            "upload_errors": errors,
            "uploaded": uploaded == 1,
            "collection_updated": (
                updated == 1
            ),
            "search_query": search_query,
            "search_mode": search_mode,
            "search_active": bool(
                search_query
            ),
            "search_count": len(
                documents
            ),
            "search_scores": search_scores,
            "score_label": score_label,
            "hybrid_lexical_weight": (
                HYBRID_LEXICAL_WEIGHT
            ),
            "hybrid_semantic_weight": (
                HYBRID_SEMANTIC_WEIGHT
            ),
        },
    )

    if new_cookie_needed:
        return set_csrf_cookie(
            response=response,
            csrf_token=csrf_token,
        )

    return response