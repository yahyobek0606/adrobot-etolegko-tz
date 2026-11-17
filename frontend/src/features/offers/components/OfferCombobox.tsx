import { CheckIcon, ChevronsUpDownIcon, LoaderCircleIcon } from 'lucide-react'
import { useId, useState } from 'react'

import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useOfferSearch } from '@/features/offers/api/queries'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import type { Offer } from '@/lib/api/types'
import { cn } from '@/lib/utils'

const SEARCH_DEBOUNCE_MS = 300

interface OfferComboboxProps {
  id?: string
  value: Offer | null
  onChange: (offer: Offer) => void
  excludeIds?: readonly number[]
  invalid?: boolean
}

export function OfferCombobox({
  id,
  value,
  onChange,
  excludeIds = [],
  invalid,
}: OfferComboboxProps) {
  const listId = useId()
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const query = useDebouncedValue(search.trim(), SEARCH_DEBOUNCE_MS)
  const { data: offers = [], isFetching, isError } = useOfferSearch(query, open)
  const visible = offers.filter((offer) => !excludeIds.includes(offer.id))

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-invalid={invalid}
          className="h-auto min-h-9 w-full justify-between bg-card py-2 text-left font-normal"
        >
          {value ? (
            <span className="min-w-0 truncate">{value.name}</span>
          ) : (
            <span className="text-muted-foreground">Search by offer name or ID</span>
          )}
          <ChevronsUpDownIcon className="text-muted-foreground" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-(--radix-popover-trigger-width) min-w-80 p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput value={search} onValueChange={setSearch} placeholder="Offer name or ID" />
          <CommandList id={listId}>
            {isFetching && visible.length === 0 ? (
              <div className="flex items-center gap-2 px-3 py-6 text-sm text-muted-foreground">
                <LoaderCircleIcon className="size-4 animate-spin" />
                Searching offers
              </div>
            ) : (
              <CommandEmpty>
                {isError ? 'Could not load offers from Keitaro.' : 'No offers match this search.'}
              </CommandEmpty>
            )}
            <CommandGroup>
              {visible.map((offer) => (
                <CommandItem
                  key={offer.id}
                  value={String(offer.id)}
                  onSelect={() => {
                    onChange(offer)
                    setOpen(false)
                  }}
                  className="items-start"
                >
                  <CheckIcon
                    className={cn('mt-0.5', value?.id === offer.id ? 'opacity-100' : 'opacity-0')}
                  />
                  <div className="min-w-0">
                    <div className="line-clamp-2 break-words">{offer.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {[offer.group, offer.countries.join(', ')].filter(Boolean).join(' / ')}
                    </div>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
