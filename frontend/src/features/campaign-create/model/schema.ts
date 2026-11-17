import { z } from 'zod'

import type { CampaignCreateRequest, Offer } from '@/lib/api/types'
import { parseCountryCodes } from '@/lib/countries'

const requiredId = (label: string) => z.string().min(1, `Choose a ${label}`)

export const campaignCreateSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Enter a campaign name')
    .max(200, 'Keep the name under 200 characters'),
  geo: z.string().superRefine((value, ctx) => {
    const { codes, invalid } = parseCountryCodes(value)
    if (invalid.length > 0) {
      ctx.addIssue({
        code: 'custom',
        message: `Not a country code: ${invalid.join(', ')}. Use two-letter codes like AU or MX.`,
      })
    } else if (codes.length === 0) {
      ctx.addIssue({ code: 'custom', message: 'Enter at least one country code' })
    }
  }),
  offer: z.custom<Offer | null>().refine((offer) => offer !== null, 'Choose an offer'),
  domainId: requiredId('domain'),
  groupId: requiredId('group'),
  trafficSourceId: requiredId('traffic source'),
})

export type CampaignCreateValues = z.input<typeof campaignCreateSchema>

export const emptyCampaignCreateValues: CampaignCreateValues = {
  name: '',
  geo: '',
  offer: null,
  domainId: '',
  groupId: '',
  trafficSourceId: '',
}

export function toCreateRequest(values: CampaignCreateValues): CampaignCreateRequest {
  if (!values.offer) throw new Error('Offer is required')
  return {
    name: values.name.trim(),
    countries: parseCountryCodes(values.geo).codes,
    offer_id: values.offer.id,
    domain_id: Number(values.domainId),
    group_id: Number(values.groupId),
    traffic_source_id: Number(values.trafficSourceId),
  }
}
