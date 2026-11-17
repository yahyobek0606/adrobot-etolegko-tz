import { ArchiveRestoreIcon, PinIcon, PinOffIcon, Trash2Icon } from 'lucide-react'
import type { Dispatch } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { ShareInput } from '@/features/campaign-editor/components/ShareInput'
import { segmentColor } from '@/features/campaign-editor/components/ShareSplitBar'
import type { DraftAction, DraftRow } from '@/features/campaign-editor/model/draft'
import { cn } from '@/lib/utils'

interface OffersTableProps {
  rows: DraftRow[]
  dispatch: Dispatch<DraftAction>
}

export function OffersTable({ rows, dispatch }: OffersTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="pl-6">Offer</TableHead>
          <TableHead className="w-44">Share (%)</TableHead>
          <TableHead className="w-28 pr-6 text-right">Action</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row, index) => {
          const colorIndex = row.isArchived ? null : index
          return (
            <TableRow key={row.offerId} className={cn(row.isArchived && 'bg-muted/40')}>
              <TableCell className="pl-6 whitespace-normal">
                <div className="flex items-start gap-3">
                  <span
                    aria-hidden
                    className="mt-1.5 size-2.5 shrink-0 rounded-full"
                    style={{
                      background: colorIndex === null ? 'var(--border)' : segmentColor(colorIndex),
                    }}
                  />
                  <div className="min-w-0">
                    <div
                      className={cn(
                        'break-words',
                        row.isArchived && 'text-muted-foreground line-through decoration-1',
                      )}
                    >
                      {row.name}
                    </div>
                    {row.isArchived && (
                      <Badge variant="outline" className="mt-1">
                        Archived
                      </Badge>
                    )}
                  </div>
                </div>
              </TableCell>
              <TableCell>
                {row.effectiveShare === null ? (
                  <span className="text-muted-foreground">Not receiving traffic</span>
                ) : (
                  <div className="flex items-center gap-1">
                    <ShareInput
                      value={row.effectiveShare}
                      label={`Share for ${row.name}`}
                      onChange={(share) =>
                        dispatch({ type: 'setShare', offerId: row.offerId, share })
                      }
                    />
                    <PinToggle row={row} share={row.effectiveShare} dispatch={dispatch} />
                  </div>
                )}
              </TableCell>
              <TableCell className="pr-6 text-right">
                {row.isArchived ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => dispatch({ type: 'restore', offerId: row.offerId })}
                  >
                    <ArchiveRestoreIcon />
                    Restore
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => dispatch({ type: 'archive', offerId: row.offerId })}
                    aria-label={`Delete ${row.name}`}
                  >
                    <Trash2Icon />
                    Delete
                  </Button>
                )}
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}

interface PinToggleProps {
  row: DraftRow
  share: number
  dispatch: Dispatch<DraftAction>
}

function PinToggle({ row, share, dispatch }: PinToggleProps) {
  const label = row.isPinned ? `Unpin share for ${row.name}` : `Pin share for ${row.name}`
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant={row.isPinned ? 'secondary' : 'ghost'}
          size="icon"
          aria-pressed={row.isPinned}
          aria-label={label}
          className={cn(row.isPinned ? 'text-primary' : 'text-muted-foreground')}
          onClick={() => dispatch({ type: 'togglePin', offerId: row.offerId, currentShare: share })}
        >
          {row.isPinned ? <PinIcon /> : <PinOffIcon />}
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        {row.isPinned
          ? 'Pinned: keeps this share when offers are added or removed'
          : 'Pin to keep this share when offers are added or removed'}
      </TooltipContent>
    </Tooltip>
  )
}
