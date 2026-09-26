from fastapi import APIRouter

from api.v1.endpoints import meeting

api_router = APIRouter()

api_router.include_router(meeting.router, tags=["meetings"])
