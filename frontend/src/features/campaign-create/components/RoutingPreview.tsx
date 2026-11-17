import type { ReactNode } from 'react'

import type { Offer } from '@/lib/api/types'
import { countryName } from '@/lib/countries'
import { cn } from '@/lib/utils'

interface RoutingPreviewProps {
  countries: string[]
  offer: Offer | null
  redirectUrl: string | undefined
}

export function RoutingPreview({ countries, offer, redirectUrl }: RoutingPreviewProps) {
  const redirectHost = redirectUrl ? new URL(redirectUrl).host : 'google.com'
  const audience =
    countries.length > 0 ? countries.map(countryName).join(', ') : 'the countries you enter'

  return (
    <section aria-labelledby="routing-preview-title" className="rounded-xl bg-card p-6 shadow-xs">
      <h2 id="routing-preview-title" className="text-base font-semibold">
        How visitors will be routed
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Keitaro checks flows top to bottom and sends each visitor down the first one that matches.
      </p>

      <div className="relative mt-6">
        <span aria-hidden className="absolute top-2 bottom-8 left-[0.6875rem] w-px bg-border" />
        <ol className="space-y-5 pl-8">
          <Flow
            tone="geo"
            title="Flow 1"
            condition={<>Visitors from {audience}</>}
            destination={redirectHost}
            filled={countries.length > 0}
          />
          <Flow
            tone="offer"
            title="Flow 2"
            condition="Everyone else"
            destination={offer ? offer.name : 'The offer you choose'}
            share={offer ? 100 : undefined}
            filled={offer !== null}
          />
        </ol>
      </div>
    </section>
  )
}

interface FlowProps {
  tone: 'geo' | 'offer'
  title: string
  condition: ReactNode
  destination: string
  share?: number
  filled: boolean
}

function Flow({ tone, title, condition, destination, share, filled }: FlowProps) {
  const toneClasses =
    tone === 'geo'
      ? { dot: 'bg-route-geo', panel: 'bg-route-geo-soft', text: 'text-route-geo' }
      : { dot: 'bg-route-offer', panel: 'bg-route-offer-soft', text: 'text-route-offer' }

  return (
    <li className="relative">
      <span
        aria-hidden
        className={cn(
          'absolute top-1.5 -left-8 size-[1.375rem] rounded-full border-4 border-card transition-colors',
          filled ? toneClasses.dot : 'bg-border',
        )}
      />
      <div
        className={cn(
          'rounded-lg px-4 py-3 transition-colors',
          filled ? toneClasses.panel : 'bg-muted',
        )}
      >
        <div
          className={cn('text-xs font-medium', filled ? toneClasses.text : 'text-muted-foreground')}
        >
          {title}
        </div>
        <div className="mt-1 text-sm">{condition}</div>
        <div className="mt-2 flex items-baseline gap-3">
          <span
            className={cn(
              'min-w-0 flex-1 font-medium break-words',
              !filled && 'text-muted-foreground',
            )}
          >
            {destination}
          </span>
          {share !== undefined && (
            <span className={cn('font-semibold tabular-nums', toneClasses.text)}>{share}%</span>
          )}
        </div>
      </div>
    </li>
  )
}
