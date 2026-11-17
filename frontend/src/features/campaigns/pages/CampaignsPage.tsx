import { PlusIcon } from 'lucide-react'
import { Link } from 'react-router'

import { paths } from '@/app/paths'
import { PageHeader } from '@/components/PageHeader'
import { QueryErrorState } from '@/components/QueryErrorState'
import { Button } from '@/components/ui/button'
import { Kbd } from '@/components/ui/kbd'
import { Skeleton } from '@/components/ui/skeleton'
import { useCampaignFormOptions, useCampaigns } from '@/features/campaigns/api/queries'
import { CampaignTable } from '@/features/campaigns/components/CampaignTable'

export function CampaignsPage() {
  const campaigns = useCampaigns()
  const options = useCampaignFormOptions()

  return (
    <>
      <PageHeader
        title="Campaigns"
        description="Campaigns in Keitaro. Open one to manage its offers and shares."
        actions={
          <Button asChild>
            <Link to={paths.campaignCreate}>
              <PlusIcon />
              New campaign
              <Kbd className="ml-1 bg-primary-foreground/20 text-primary-foreground">N</Kbd>
            </Link>
          </Button>
        }
      />
      {campaigns.isPending ? (
        <Skeleton className="h-96 w-full rounded-xl" />
      ) : campaigns.isError ? (
        <QueryErrorState
          title="Could not load campaigns from Keitaro"
          error={campaigns.error}
          onRetry={() => void campaigns.refetch()}
        />
      ) : (
        <CampaignTable
          campaigns={campaigns.data}
          groups={options.data?.groups ?? []}
          defaultGroupId={options.data?.defaults.group_id}
        />
      )}
    </>
  )
}
