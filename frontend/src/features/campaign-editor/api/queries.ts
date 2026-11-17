import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { CampaignOfferInput, CampaignOffersState } from '@/lib/api/types'

export const campaignOfferKeys = {
  all: ['campaign-offers'] as const,
  detail: (campaignId: number) => [...campaignOfferKeys.all, campaignId] as const,
}

const forCampaign = (campaignId: number) => ({ params: { path: { campaign_id: campaignId } } })

export function useCampaignOffers(campaignId: number) {
  return useQuery({
    queryKey: campaignOfferKeys.detail(campaignId),
    queryFn: () =>
      unwrap(api.GET('/api/v1/campaigns/{campaign_id}/offers', forCampaign(campaignId))),
    staleTime: Infinity,
  })
}

function useStoreState(campaignId: number) {
  const queryClient = useQueryClient()
  return (state: CampaignOffersState) =>
    queryClient.setQueryData(campaignOfferKeys.detail(campaignId), state)
}

export function useSyncCampaignOffers(campaignId: number) {
  const store = useStoreState(campaignId)
  return useMutation({
    mutationFn: () =>
      unwrap(api.POST('/api/v1/campaigns/{campaign_id}/offers/sync', forCampaign(campaignId))),
    onSuccess: store,
  })
}

export function usePushCampaignOffers(campaignId: number) {
  const store = useStoreState(campaignId)
  return useMutation({
    mutationFn: (offers: CampaignOfferInput[]) =>
      unwrap(
        api.PUT('/api/v1/campaigns/{campaign_id}/offers', {
          ...forCampaign(campaignId),
          body: { offers },
        }),
      ),
    onSuccess: store,
  })
}
