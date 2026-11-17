import { TriangleAlertIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { errorMessage } from '@/lib/api/errors'

interface QueryErrorStateProps {
  title: string
  error: unknown
  onRetry: () => void
}

export function QueryErrorState({ title, error, onRetry }: QueryErrorStateProps) {
  return (
    <div role="alert" className="flex max-w-xl gap-3 rounded-xl bg-card p-5 shadow-xs">
      <TriangleAlertIcon className="mt-0.5 size-5 shrink-0 text-destructive" />
      <div className="min-w-0">
        <p className="font-medium">{title}</p>
        <p className="mt-1 text-sm break-words text-muted-foreground">{errorMessage(error)}</p>
        <Button variant="outline" size="sm" className="mt-3" onClick={onRetry}>
          Try again
        </Button>
      </div>
    </div>
  )
}
