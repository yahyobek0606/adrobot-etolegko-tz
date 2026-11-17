import type { Campaign, CampaignFormOptions, CampaignOffersState, Offer } from '@/lib/api/types'

export const formOptions: CampaignFormOptions = {
  domains: [{ id: 1813, name: 'kylovoa.com' }],
  groups: [
    { id: 10332, name: 'FORTESTS' },
    { id: 9799, name: 'Other group' },
  ],
  traffic_sources: [{ id: 836, name: 'FORTESTS' }],
  defaults: { domain_id: 1813, group_id: 10332, traffic_source_id: 836 },
  fallback_redirect_url: 'https://google.com/',
}

export const offers: Offer[] = [
  { id: 13972, name: '13972 Flexacil [JOINT-PE]', group: 'JO Flexacil PE', countries: ['Peru'] },
  { id: 3749, name: '3749 Miaflow [BEAUTY-RO]', group: 'BE Miaflow RO', countries: ['Romania'] },
]

export const campaigns: Campaign[] = [
  {
    id: 101,
    name: 'Test AU campaign',
    alias: 'test-au-campaign-ab12cd',
    is_active: true,
    tracking_url: 'https://kylovoa.com/test-au-campaign-ab12cd',
    admin_url: 'https://tracker.test/admin/#!/campaign/101/main',
    group_id: 10332,
  },
  {
    id: 102,
    name: 'Someone else',
    alias: 'someone-else',
    is_active: false,
    tracking_url: 'https://kylovoa.com/someone-else',
    admin_url: 'https://tracker.test/admin/#!/campaign/102/main',
    group_id: 9799,
  },
]

export const campaignOffers: CampaignOffersState = {
  campaign: campaigns[0]!,
  stream: { id: 501, name: 'Offers' },
  offers: [
    {
      offer_id: 13972,
      name: '13972 Flexacil [JOINT-PE]',
      share: 50,
      is_pinned: true,
      is_archived: false,
    },
    {
      offer_id: 24800,
      name: '24800 Flexacil [land es]',
      share: 50,
      is_pinned: false,
      is_archived: false,
    },
    { offer_id: 16361, name: '16361 Old offer', share: 20, is_pinned: false, is_archived: true },
  ],
  revision: 'rev-1',
}
