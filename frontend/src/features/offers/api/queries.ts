import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'

export const offerKeys = {
  all: ['offers'] as const,
  search: (query: string) => [...offerKeys.all, 'search', query] as const,
}

export const OFFER_SEARCH_LIMIT = 20

export function useOfferSearch(query: string, enabled = true) {
  return useQuery({
    queryKey: offerKeys.search(query),
    queryFn: () =>
      unwrap(
        api.GET('/api/v1/offers', { params: { query: { query, limit: OFFER_SEARCH_LIMIT } } }),
      ),
    placeholderData: keepPreviousData,
    enabled,
  })
}
