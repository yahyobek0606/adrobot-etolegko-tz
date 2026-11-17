import { http, HttpResponse } from 'msw'

import { campaignOffers, campaigns, formOptions, offers } from '@/test/fixtures'

export const handlers = [
  http.get('*/api/v1/campaigns/:campaignId/offers', () => HttpResponse.json(campaignOffers)),
  http.get('*/api/v1/campaigns/form-options', () => HttpResponse.json(formOptions)),
  http.get('*/api/v1/campaigns', () => HttpResponse.json(campaigns)),
  http.get('*/api/v1/offers', ({ request }) => {
    const query = new URL(request.url).searchParams.get('query')?.toLowerCase() ?? ''
    return HttpResponse.json(offers.filter((offer) => offer.name.toLowerCase().includes(query)))
  }),
]
