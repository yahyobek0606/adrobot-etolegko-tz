import type { RouteObject } from 'react-router'

import { AppLayout } from '@/app/AppLayout'
import { paths } from '@/app/paths'
import { CampaignCreatePage } from '@/features/campaign-create/pages/CampaignCreatePage'
import { CampaignEditorPage } from '@/features/campaign-editor/pages/CampaignEditorPage'
import { CampaignsPage } from '@/features/campaigns/pages/CampaignsPage'

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      { path: paths.campaigns, element: <CampaignsPage /> },
      { path: paths.campaignCreate, element: <CampaignCreatePage /> },
      { path: paths.campaignEditor(':campaignId'), element: <CampaignEditorPage /> },
    ],
  },
]
