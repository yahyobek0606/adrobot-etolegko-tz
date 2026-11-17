import {
  ArrowLeftIcon,
  CircleAlertIcon,
  ExternalLinkIcon,
  LoaderCircleIcon,
  RefreshCwIcon,
  UploadIcon,
} from 'lucide-react'
import { useMemo, useReducer, useState } from 'react'
import { Link } from 'react-router'
import { toast } from 'sonner'

import { paths } from '@/app/paths'
import { shortcuts } from '@/app/shortcuts'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { PageHeader } from '@/components/PageHeader'
import { Button } from '@/components/ui/button'
import { Kbd } from '@/components/ui/kbd'
import {
  usePushCampaignOffers,
  useSyncCampaignOffers,
} from '@/features/campaign-editor/api/queries'
import { AddOfferDialog } from '@/features/campaign-editor/components/AddOfferDialog'
import { OffersTable } from '@/features/campaign-editor/components/OffersTable'
import { ShareSplitBar } from '@/features/campaign-editor/components/ShareSplitBar'
import { UnsavedChangesGuard } from '@/features/campaign-editor/components/UnsavedChangesGuard'
import {
  buildView,
  draftReducer,
  fromServer,
  isDirty,
  toRequest,
} from '@/features/campaign-editor/model/draft'
import { shareErrorMessages } from '@/features/campaign-editor/model/messages'
import { modKeyLabel, useHotkey } from '@/hooks/useHotkey'
import { errorMessage, isConflict } from '@/lib/api/errors'
import type { CampaignOffersState } from '@/lib/api/types'
import { cn } from '@/lib/utils'

interface CampaignOffersEditorProps {
  state: CampaignOffersState
}

export function CampaignOffersEditor({ state }: CampaignOffersEditorProps) {
  const [draft, dispatch] = useReducer(draftReducer, state.offers, fromServer)
  const view = useMemo(() => buildView(draft), [draft])
  const dirty = isDirty(view, state.offers)
  const push = usePushCampaignOffers(state.campaign.id)
  const sync = useSyncCampaignOffers(state.campaign.id)
  const [confirmSync, setConfirmSync] = useState(false)
  const busy = push.isPending || sync.isPending
  const canPush = dirty && view.error === null && !busy && state.stream !== null

  const reset = () => dispatch({ type: 'reset', offers: fromServer(state.offers) })
  const pushChanges = () =>
    push.mutate(
      { offers: toRequest(view), revision: state.revision },
      {
        onSuccess: () => toast.success('Changes pushed to Keitaro'),
        onError: (error) =>
          toast.error('Changes were not pushed', {
            description: errorMessage(error),
            action: isConflict(error)
              ? { label: 'Fetch from KT', onClick: () => setConfirmSync(true) }
              : undefined,
          }),
      },
    )

  const fetchFromKeitaro = () => {
    setConfirmSync(false)
    sync.mutate(undefined, {
      onSuccess: () => toast.success('Fetched streams from Keitaro'),
      onError: (error) =>
        toast.error('Could not fetch streams from Keitaro', { description: errorMessage(error) }),
    })
  }
  const requestFetch = () => (dirty ? setConfirmSync(true) : fetchFromKeitaro())

  useHotkey(shortcuts.pushChanges, () => {
    if (canPush) pushChanges()
  })
  useHotkey(shortcuts.fetchFromKeitaro, requestFetch, { enabled: !busy })
  useHotkey(shortcuts.viewInKeitaro, () =>
    window.open(state.campaign.admin_url, '_blank', 'noopener,noreferrer'),
  )

  return (
    <>
      <Link
        to={paths.campaigns}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeftIcon className="size-4" />
        All campaigns
      </Link>
      <PageHeader
        title={state.campaign.name}
        description={<span className="break-all">{state.campaign.tracking_url}</span>}
        actions={
          <>
            <Button variant="outline" disabled={busy} onClick={requestFetch} aria-keyshortcuts="F">
              <RefreshCwIcon className={cn(sync.isPending && 'animate-spin')} />
              Fetch streams from KT
              <Kbd className="ml-1">F</Kbd>
            </Button>
            <Button variant="outline" asChild>
              <a
                href={state.campaign.admin_url}
                target="_blank"
                rel="noreferrer"
                aria-keyshortcuts="V"
              >
                <ExternalLinkIcon />
                View in KT
                <Kbd className="ml-1">V</Kbd>
              </a>
            </Button>
          </>
        }
      />
      <ConfirmDialog
        open={confirmSync}
        title="Discard changes and fetch from Keitaro?"
        description="Fetching replaces this table with the current state in Keitaro. Your unpushed changes will be lost."
        confirmLabel="Discard and fetch"
        onConfirm={fetchFromKeitaro}
        onCancel={() => setConfirmSync(false)}
      />
      <UnsavedChangesGuard when={dirty} />
      <section aria-labelledby="offers-title" className="rounded-xl bg-card shadow-xs">
        <div className="flex flex-wrap items-start justify-between gap-4 p-6 pb-4">
          <div>
            <h2 id="offers-title" className="text-lg font-semibold">
              Offers
            </h2>
            <p className="text-sm text-muted-foreground">
              {state.stream
                ? `Traffic of the “${state.stream.name}” flow, split between ${view.active.length.toString()} active offers.`
                : 'This campaign has no offers flow in Keitaro.'}
            </p>
          </div>
          <AddOfferDialog
            activeOfferIds={view.active.map((row) => row.offerId)}
            onAdd={(offer) => dispatch({ type: 'add', offerId: offer.id, name: offer.name })}
          />
        </div>

        <div className="px-6 pb-6">
          <ShareSplitBar rows={view.active} invalid={view.error !== null} />
        </div>

        {view.rows.length > 0 ? (
          <OffersTable rows={view.rows} dispatch={dispatch} />
        ) : (
          <p className="border-t px-6 py-10 text-center text-muted-foreground">
            No offers yet. Add one to start sending traffic.
          </p>
        )}

        <div
          className={cn(
            'sticky bottom-0 flex flex-wrap items-center gap-3 rounded-b-xl border-t bg-card/95 px-6 py-4 backdrop-blur',
            dirty && 'border-t-primary/40',
          )}
        >
          <div role="status" aria-live="polite" className="mr-auto flex items-center gap-2 text-sm">
            {view.error ? (
              <>
                <CircleAlertIcon className="size-4 shrink-0 text-destructive" />
                <span className="text-destructive">{shareErrorMessages[view.error]}</span>
              </>
            ) : dirty ? (
              <>
                <span className="size-2 rounded-full bg-primary motion-safe:animate-pulse" />
                <span className="font-medium">Unsaved changes</span>
              </>
            ) : (
              <span className="text-muted-foreground">In sync with Keitaro</span>
            )}
          </div>
          <Button variant="outline" disabled={!dirty || busy} onClick={reset}>
            Cancel
          </Button>
          <Button disabled={!canPush} onClick={pushChanges} aria-keyshortcuts="Control+S Meta+S">
            {push.isPending ? <LoaderCircleIcon className="animate-spin" /> : <UploadIcon />}
            Push changes
            <Kbd className="ml-1 bg-primary-foreground/20 text-primary-foreground">
              {modKeyLabel} S
            </Kbd>
          </Button>
        </div>
      </section>
    </>
  )
}
