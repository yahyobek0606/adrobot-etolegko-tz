import type { components } from '@/lib/api/schema'

type Schemas = components['schemas']

export type Campaign = Schemas['CampaignResponse']
export type CampaignCreateRequest = Schemas['CampaignCreateRequest']
export type CampaignFormOptions = Schemas['CampaignFormOptionsResponse']
export type NamedRef = Schemas['NamedRefResponse']
export type Offer = Schemas['OfferResponse']
export type CampaignOffer = Schemas['CampaignOfferResponse']
export type CampaignOfferInput = Schemas['CampaignOfferInput']
export type CampaignOffersUpdate = Schemas['CampaignOffersUpdateRequest']
export type CampaignOffersState = Schemas['CampaignOffersResponse']
