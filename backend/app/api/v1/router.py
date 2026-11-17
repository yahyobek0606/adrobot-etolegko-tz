from fastapi import APIRouter

from app.api.v1 import campaign_offers, campaigns, health, offers

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(campaigns.router)
api_router.include_router(offers.router)
api_router.include_router(campaign_offers.router)
