from fastapi import APIRouter

from app.api.v1.schemas import CampaignOffersResponse, CampaignOffersUpdateRequest
from app.core.dependencies import CampaignOffersDep
from app.services.campaign_offers import OfferDraft

router = APIRouter(prefix="/campaigns/{campaign_id}/offers", tags=["campaign offers"])


@router.get("", response_model=CampaignOffersResponse)
async def get_campaign_offers(
    campaign_id: int, service: CampaignOffersDep
) -> CampaignOffersResponse:
    return CampaignOffersResponse.from_state(await service.get_state(campaign_id))


@router.post("/sync", response_model=CampaignOffersResponse)
async def sync_campaign_offers(
    campaign_id: int, service: CampaignOffersDep
) -> CampaignOffersResponse:
    return CampaignOffersResponse.from_state(await service.sync(campaign_id))


@router.put("", response_model=CampaignOffersResponse)
async def update_campaign_offers(
    campaign_id: int, payload: CampaignOffersUpdateRequest, service: CampaignOffersDep
) -> CampaignOffersResponse:
    drafts = [
        OfferDraft(
            offer_id=offer.offer_id,
            share=offer.share,
            is_pinned=offer.is_pinned,
            is_archived=offer.is_archived,
        )
        for offer in payload.offers
    ]
    return CampaignOffersResponse.from_state(await service.push(campaign_id, drafts))
