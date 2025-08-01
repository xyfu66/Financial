"""
Main API router for version 1
"""

from fastapi import APIRouter
from .endpoints import auth, users, income, expense, notifications, system, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(income.router, prefix="/income", tags=["income"])
api_router.include_router(expense.router, prefix="/expense", tags=["expense"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])