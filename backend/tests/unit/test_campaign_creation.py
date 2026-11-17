from dataclasses import replace

import pytest

from app.domain.errors import NotFoundError, ProviderError
from app.providers.base import StreamKind, StreamOffer
from app.services.campaign_creation import CampaignCreationService, CreateCampaignCommand
from tests.fakes import FakeTrackerProvider

COMMAND = CreateCampaignCommand(
    name="My campaign",
    countries=["AU", "MX"],
    offer_id=13972,
    domain_id=1813,
    group_id=10332,
    traffic_source_id=836,
)


@pytest.fixture
def provider() -> FakeTrackerProvider:
    return FakeTrackerProvider()


@pytest.fixture
def service(provider: FakeTrackerProvider) -> CampaignCreationService:
    return CampaignCreationService(
        provider, "https://google.com/", alias_factory=lambda name: "my-campaign-abc123"
    )


async def test_creates_campaign_with_geo_and_offer_streams(
    service: CampaignCreationService, provider: FakeTrackerProvider
) -> None:
    campaign = await service.create(COMMAND)

    assert campaign.alias == "my-campaign-abc123"
    assert (campaign.domain_id, campaign.group_id, campaign.traffic_source_id) == (1813, 10332, 836)

    geo, offers = await provider.list_streams(campaign.id)
    assert geo.kind is StreamKind.GEO_REDIRECT
    assert geo.position == 1
    assert geo.countries == ["AU", "MX"]
    assert geo.redirect_url == "https://google.com/"
    assert geo.name == "AU, MX → google.com"
    assert offers.kind is StreamKind.OFFERS
    assert offers.position == 2
    assert offers.offers == [StreamOffer(offer_id=13972, share=100)]


async def test_unknown_offer_is_rejected_before_anything_is_created(
    service: CampaignCreationService, provider: FakeTrackerProvider
) -> None:
    with pytest.raises(NotFoundError):
        await service.create(replace(COMMAND, offer_id=1))

    assert provider.campaigns == {}


@pytest.mark.parametrize("failing", ["create_geo_redirect_stream", "create_offers_stream"])
async def test_stream_failure_archives_the_campaign(
    service: CampaignCreationService, provider: FakeTrackerProvider, failing: str
) -> None:
    provider.fail_on.add(failing)

    with pytest.raises(ProviderError):
        await service.create(COMMAND)

    assert provider.campaigns == {}
    assert len(provider.archived_campaign_ids) == 1


async def test_rollback_failure_keeps_original_error(
    service: CampaignCreationService, provider: FakeTrackerProvider
) -> None:
    provider.fail_on.update({"create_offers_stream", "archive_campaign"})

    with pytest.raises(ProviderError, match="create_offers_stream"):
        await service.create(COMMAND)
