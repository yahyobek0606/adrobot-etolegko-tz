import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { CampaignCreateRequest } from '@/lib/api/types'

export const campaignKeys = {
  all: ['campaigns'] as const,
  list: () => [...campaignKeys.all, 'list'] as const,
  formOptions: () => [...campaignKeys.all, 'form-options'] as const,
}

export function useCampaigns() {
  return useQuery({
    queryKey: campaignKeys.list(),
    queryFn: () => unwrap(api.GET('/api/v1/campaigns')),
  })
}

export function useCampaignFormOptions() {
  return useQuery({
    queryKey: campaignKeys.formOptions(),
    queryFn: () => unwrap(api.GET('/api/v1/campaigns/form-options')),
    staleTime: 5 * 60_000,
  })
}

export function useCreateCampaign() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: CampaignCreateRequest) => unwrap(api.POST('/api/v1/campaigns', { body })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: campaignKeys.list() }),
  })
}
