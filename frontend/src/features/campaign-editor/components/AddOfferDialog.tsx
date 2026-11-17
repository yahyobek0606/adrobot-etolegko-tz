import { PlusIcon } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { OfferCombobox } from '@/features/offers/components/OfferCombobox'
import type { Offer } from '@/lib/api/types'

interface AddOfferDialogProps {
  activeOfferIds: readonly number[]
  onAdd: (offer: Offer) => void
}

export function AddOfferDialog({ activeOfferIds, onAdd }: AddOfferDialogProps) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <PlusIcon />
          Add offer
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add offer</DialogTitle>
          <DialogDescription>
            Search Keitaro offers by name or ID. Unpinned shares are rebalanced automatically; an
            archived offer is restored instead of added twice.
          </DialogDescription>
        </DialogHeader>
        <OfferCombobox
          value={null}
          excludeIds={activeOfferIds}
          onChange={(offer) => {
            onAdd(offer)
            setOpen(false)
          }}
        />
      </DialogContent>
    </Dialog>
  )
}
