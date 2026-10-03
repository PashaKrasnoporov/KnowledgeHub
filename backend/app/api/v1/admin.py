import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_api_admin,
    require_api_csrf,
)
from app.baza_danykh.dependencies import (
    get_db_session,
)
from app.modeli.user import User
from app.repositories.admin_repository import (
    get_all_users,
)
from app.schemas.admin_api import (
    UserActiveStatusAPIRequest,
)
from app.schemas.api import (
    UserAPIResponse,
)
from app.services.admin_service import (
    AdminActionError,
    change_user_active_status,
)


router = APIRouter(
    prefix="/admin",
    tags=["API admin"],
)

logger = logging.getLogger(__name__)


@router.get(
    "/users",
    response_model=list[UserAPIResponse],
    summary="List all users",
)
def api_admin_users(
    admin_user: User = Depends(
        get_api_admin
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    del admin_user

    return get_all_users(
        session=session
    )


@router.patch(
    "/users/{user_id}/active",
    response_model=UserAPIResponse,
    summary="Change user active status",
    dependencies=[
        Depends(require_api_csrf)
    ],
)
def api_change_user_active_status(
    user_id: int,
    payload: UserActiveStatusAPIRequest,
    admin_user: User = Depends(
        get_api_admin
    ),
    session: Session = Depends(
        get_db_session
    ),
):
    try:
        user = change_user_active_status(
            session=session,
            admin_user=admin_user,
            target_user_id=user_id,
            is_active=payload.is_active,
        )

    except AdminActionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Адміністратор не може деактивувати "
                "власний обліковий запис."
            ),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Database error during API admin action."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не вдалося виконати адміністративну дію.",
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user
