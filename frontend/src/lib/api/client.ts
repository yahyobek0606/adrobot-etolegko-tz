import createClient from 'openapi-fetch'

import type { paths } from '@/lib/api/schema'

export const api = createClient<paths>({
  baseUrl: window.location.origin,
  fetch: (request) => globalThis.fetch(request),
})
