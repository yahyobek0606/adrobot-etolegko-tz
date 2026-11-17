from fastapi import APIRouter, status

from app.api.v1.schemas import (
    CampaignCreateRequest,
    CampaignFormOptionsResponse,
    CampaignResponse,
)
from app.core.dependencies import CampaignCatalogDep, CampaignCreationDep
from app.services.campaign_creation import CreateCampaignCommand

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(catalog: CampaignCatalogDep) -> list[CampaignResponse]:
    return [CampaignResponse.from_summary(summary) for summary in await catalog.list_campaigns()]


@router.get("/form-options", response_model=CampaignFormOptionsResponse)
async def campaign_form_options(catalog: CampaignCatalogDep) -> CampaignFormOptionsResponse:
    return CampaignFormOptionsResponse.from_options(await catalog.form_options())


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreateRequest,
    creation: CampaignCreationDep,
    catalog: CampaignCatalogDep,
) -> CampaignResponse:
    campaign = await creation.create(
        CreateCampaignCommand(
            name=payload.name,
            countries=payload.countries,
            offer_id=payload.offer_id,
            domain_id=payload.domain_id,
            group_id=payload.group_id,
            traffic_source_id=payload.traffic_source_id,
        )
    )
    return CampaignResponse.from_summary(catalog.summarize(campaign))
