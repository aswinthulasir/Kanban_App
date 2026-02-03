from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .boards import router as boards_router
from .columns import router as columns_router
from .tasks import router as tasks_router
from .comments import router as comments_router
from .attachments import router as attachments_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(boards_router, prefix="/boards", tags=["boards"])
api_router.include_router(columns_router, prefix="/columns", tags=["columns"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(comments_router, prefix="/comments", tags=["comments"])
api_router.include_router(attachments_router, prefix="/attachments", tags=["attachments"])
