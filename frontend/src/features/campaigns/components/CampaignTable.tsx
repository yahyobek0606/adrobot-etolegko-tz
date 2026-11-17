import { ChevronRightIcon, ExternalLinkIcon, SearchIcon } from 'lucide-react'
import { useMemo, useRef, useState } from 'react'
import { Link } from 'react-router'

import { paths } from '@/app/paths'
import { shortcuts } from '@/app/shortcuts'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { InputGroup, InputGroupAddon, InputGroupInput } from '@/components/ui/input-group'
import { Kbd } from '@/components/ui/kbd'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { modKeyLabel, useHotkey } from '@/hooks/useHotkey'
import type { Campaign, NamedRef } from '@/lib/api/types'

const ALL_GROUPS = 'all'

interface CampaignTableProps {
  campaigns: Campaign[]
  groups: NamedRef[]
  defaultGroupId: number | undefined
}

export function CampaignTable({ campaigns, groups, defaultGroupId }: CampaignTableProps) {
  const [search, setSearch] = useState('')
  const searchRef = useRef<HTMLInputElement>(null)
  useHotkey(shortcuts.search, () => {
    searchRef.current?.focus()
    searchRef.current?.select()
  })
  const [groupFilter, setGroupFilter] = useState<string | null>(null)
  const activeGroup = groupFilter ?? (defaultGroupId ? String(defaultGroupId) : ALL_GROUPS)

  const groupNames = useMemo(() => new Map(groups.map((g) => [g.id, g.name])), [groups])
  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase()
    return campaigns.filter(
      (campaign) =>
        (activeGroup === ALL_GROUPS || String(campaign.group_id) === activeGroup) &&
        (!needle ||
          campaign.name.toLowerCase().includes(needle) ||
          campaign.alias.toLowerCase().includes(needle) ||
          String(campaign.id) === needle),
    )
  }, [campaigns, search, activeGroup])

  return (
    <div className="rounded-xl bg-card shadow-xs">
      <div className="flex flex-wrap items-center gap-3 border-b p-4">
        <InputGroup className="max-w-sm min-w-56 flex-1">
          <InputGroupAddon>
            <SearchIcon />
          </InputGroupAddon>
          <InputGroupInput
            ref={searchRef}
            aria-label="Search campaigns"
            aria-keyshortcuts="/ Control+K Meta+K"
            placeholder="Search by name, alias or ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                setSearch('')
                event.currentTarget.blur()
              }
            }}
          />
          <InputGroupAddon align="inline-end" className="hidden sm:flex">
            <Kbd>/</Kbd>
            <Kbd>{modKeyLabel} K</Kbd>
          </InputGroupAddon>
        </InputGroup>
        <Select value={activeGroup} onValueChange={setGroupFilter}>
          <SelectTrigger aria-label="Filter by group" className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_GROUPS}>All groups</SelectItem>
            {groups.map((group) => (
              <SelectItem key={group.id} value={String(group.id)}>
                {group.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="ml-auto text-sm text-muted-foreground tabular-nums">
          {visible.length} of {campaigns.length}
        </span>
      </div>

      {visible.length === 0 ? (
        <p className="px-4 py-12 text-center text-muted-foreground">
          No campaigns match. Clear the search or pick another group.
        </p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24 pl-4">ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="hidden md:table-cell">Group</TableHead>
              <TableHead className="hidden lg:table-cell">Tracking URL</TableHead>
              <TableHead className="w-24">Status</TableHead>
              <TableHead className="w-48 pr-4 text-right">
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {visible.map((campaign) => (
              <TableRow key={campaign.id}>
                <TableCell className="pl-4 text-muted-foreground tabular-nums">
                  {campaign.id}
                </TableCell>
                <TableCell className="max-w-72 truncate font-medium">
                  <Link
                    to={paths.campaignEditor(campaign.id)}
                    className="underline-offset-4 hover:text-primary hover:underline"
                  >
                    {campaign.name}
                  </Link>
                </TableCell>
                <TableCell className="hidden text-muted-foreground md:table-cell">
                  {campaign.group_id
                    ? (groupNames.get(campaign.group_id) ?? campaign.group_id)
                    : '—'}
                </TableCell>
                <TableCell className="hidden max-w-80 truncate text-muted-foreground lg:table-cell">
                  {campaign.tracking_url}
                </TableCell>
                <TableCell>
                  <Badge variant={campaign.is_active ? 'secondary' : 'outline'}>
                    {campaign.is_active ? 'Active' : 'Disabled'}
                  </Badge>
                </TableCell>
                <TableCell className="pr-4">
                  <div className="flex items-center justify-end gap-1">
                    <Button variant="outline" size="sm" asChild>
                      <Link
                        to={paths.campaignEditor(campaign.id)}
                        aria-label={`View details of ${campaign.name}`}
                      >
                        View details
                        <ChevronRightIcon />
                      </Link>
                    </Button>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon-sm" asChild>
                          <a
                            href={campaign.admin_url}
                            target="_blank"
                            rel="noreferrer"
                            aria-label={`Open ${campaign.name} in Keitaro`}
                          >
                            <ExternalLinkIcon />
                          </a>
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Open in Keitaro</TooltipContent>
                    </Tooltip>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
