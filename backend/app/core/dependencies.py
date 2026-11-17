from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.db.session import Database
from app.db.unit_of_work import UnitOfWork
from app.providers.base import TrackerProvider
from app.services.campaign_catalog import CampaignCatalogService, CampaignDefaults
from app.services.campaign_creation import CampaignCreationService
from app.services.campaign_offers import CampaignOffersService


def get_database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


def get_provider(request: Request) -> TrackerProvider:
    provider: TrackerProvider = request.app.state.provider
    return provider


async def get_session(
    database: Annotated[Database, Depends(get_database)],
) -> AsyncIterator[AsyncSession]:
    async for session in database.session():
        yield session


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
ProviderDep = Annotated[TrackerProvider, Depends(get_provider)]


def get_campaign_catalog(provider: ProviderDep, settings: SettingsDep) -> CampaignCatalogService:
    return CampaignCatalogService(
        provider,
        CampaignDefaults(
            domain_id=settings.keitaro_default_domain_id,
            group_id=settings.keitaro_default_group_id,
            traffic_source_id=settings.keitaro_default_traffic_source_id,
        ),
        str(settings.fallback_redirect_url),
    )


def get_campaign_creation(provider: ProviderDep, settings: SettingsDep) -> CampaignCreationService:
    return CampaignCreationService(provider, str(settings.fallback_redirect_url))


CampaignCatalogDep = Annotated[CampaignCatalogService, Depends(get_campaign_catalog)]
CampaignCreationDep = Annotated[CampaignCreationService, Depends(get_campaign_creation)]


def get_campaign_offers(provider: ProviderDep, session: SessionDep) -> CampaignOffersService:
    return CampaignOffersService(provider, UnitOfWork(session))


CampaignOffersDep = Annotated[CampaignOffersService, Depends(get_campaign_offers)]
