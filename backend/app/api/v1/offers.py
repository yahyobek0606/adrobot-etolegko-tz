from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.schemas import OfferResponse
from app.core.dependencies import CampaignCatalogDep

router = APIRouter(prefix="/offers", tags=["offers"])


@router.get("", response_model=list[OfferResponse])
async def search_offers(
    catalog: CampaignCatalogDep,
    query: Annotated[str, Query(max_length=200)] = "",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[OfferResponse]:
    return [OfferResponse.from_offer(offer) for offer in await catalog.search_offers(query, limit)]
