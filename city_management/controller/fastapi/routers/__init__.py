# -*- coding: utf-8 -*-

from fastapi import APIRouter

from .reports import router as reports_router
from .categories import router as categories_router
from .intentions import router as intentions_router
from .webhooks import router as webhooks_router

# Create main router for city management
router = APIRouter()

# Include all sub-routers
router.include_router(reports_router, prefix="/report", tags=["Reports"])
router.include_router(categories_router, prefix="/categories", tags=["Categories"])
router.include_router(intentions_router, prefix="/citizen_intention", tags=["Citizen Intentions"])
router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
