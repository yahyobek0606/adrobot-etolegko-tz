import { PinIcon } from 'lucide-react'

import type { DraftRow } from '@/features/campaign-editor/model/draft'
import { cn } from '@/lib/utils'

const LABEL_MIN_SHARE = 8

export function segmentColor(index: number): string {
  const strength = 100 - ((index * 17) % 68)
  return `color-mix(in oklch, var(--route-offer) ${strength.toString()}%, white)`
}

interface ShareSplitBarProps {
  rows: DraftRow[]
  invalid: boolean
}

export function ShareSplitBar({ rows, invalid }: ShareSplitBarProps) {
  const description = rows
    .map((row) => `offer ${row.offerId.toString()} ${(row.effectiveShare ?? 0).toString()}%`)
    .join(', ')

  return (
    <div
      role="img"
      aria-label={rows.length ? `Traffic split: ${description}` : 'No active offers'}
      className={cn(
        'flex h-12 w-full overflow-hidden rounded-lg bg-muted',
        invalid && 'ring-2 ring-destructive ring-offset-2 ring-offset-card',
      )}
    >
      {rows.map((row, index) => {
        const share = row.effectiveShare ?? 0
        return (
          <div
            key={row.offerId}
            title={`${row.name}: ${share.toString()}%`}
            className="flex min-w-0 items-center justify-center gap-1 border-r-2 border-card text-xs font-medium text-white tabular-nums transition-[flex-basis] duration-300 last:border-r-0 motion-reduce:transition-none"
            style={{ flexBasis: `${share.toString()}%`, background: segmentColor(index) }}
          >
            {share >= LABEL_MIN_SHARE && (
              <>
                {row.isPinned && <PinIcon className="size-3" />}
                <span className="truncate">{share}%</span>
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}
