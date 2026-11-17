import { useParams } from 'react-router'

import { QueryErrorState } from '@/components/QueryErrorState'
import { Skeleton } from '@/components/ui/skeleton'
import { useCampaignOffers } from '@/features/campaign-editor/api/queries'
import { CampaignOffersEditor } from '@/features/campaign-editor/components/CampaignOffersEditor'

export function CampaignEditorPage() {
  const campaignId = Number(useParams().campaignId)
  const offers = useCampaignOffers(campaignId)

  if (offers.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-80" />
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    )
  }

  if (offers.isError) {
    return (
      <QueryErrorState
        title="Could not load this campaign from Keitaro"
        error={offers.error}
        onRetry={() => void offers.refetch()}
      />
    )
  }

  return <CampaignOffersEditor key={offers.dataUpdatedAt} state={offers.data} />
}
