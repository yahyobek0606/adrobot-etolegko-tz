import { useNavigate } from 'react-router'
import { toast } from 'sonner'

import { paths } from '@/app/paths'
import { PageHeader } from '@/components/PageHeader'
import { QueryErrorState } from '@/components/QueryErrorState'
import { Skeleton } from '@/components/ui/skeleton'
import { CampaignCreateForm } from '@/features/campaign-create/components/CampaignCreateForm'
import { useCampaignFormOptions, useCreateCampaign } from '@/features/campaigns/api/queries'
import { errorMessage } from '@/lib/api/errors'

export function CampaignCreatePage() {
  const navigate = useNavigate()
  const options = useCampaignFormOptions()
  const createCampaign = useCreateCampaign()

  return (
    <>
      <PageHeader
        title="New campaign"
        description="Creates a Keitaro campaign with two flows: chosen countries go to Google, everyone else goes to your offer."
      />
      {options.isPending ? (
        <Skeleton className="h-[34rem] w-full max-w-[26rem] rounded-xl" />
      ) : options.isError ? (
        <QueryErrorState
          title="Could not load domains, groups and sources from Keitaro"
          error={options.error}
          onRetry={() => void options.refetch()}
        />
      ) : (
        <CampaignCreateForm
          options={options.data}
          isSubmitting={createCampaign.isPending}
          onSubmit={(request) =>
            createCampaign.mutate(request, {
              onSuccess: (campaign) => {
                toast.success(`Campaign “${campaign.name}” created`)
                void navigate(paths.campaignEditor(campaign.id))
              },
              onError: (error) =>
                toast.error('Campaign was not created', { description: errorMessage(error) }),
            })
          }
        />
      )}
    </>
  )
}
