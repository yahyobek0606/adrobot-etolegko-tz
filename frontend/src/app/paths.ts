export const paths = {
  campaigns: '/',
  campaignCreate: '/campaigns/new',
  campaignEditor: (campaignId: number | string) => `/campaigns/${campaignId}`,
} as const
