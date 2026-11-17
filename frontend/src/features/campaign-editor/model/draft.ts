import {
  allocateShares,
  TOTAL_SHARE,
  type ShareError,
} from '@/features/campaign-editor/model/shares'
import type { CampaignOffer, CampaignOfferInput } from '@/lib/api/types'

export interface DraftOffer {
  offerId: number
  name: string
  share: number
  isPinned: boolean
  isArchived: boolean
}

export interface DraftRow extends DraftOffer {
  effectiveShare: number | null
}

export interface DraftView {
  rows: DraftRow[]
  active: DraftRow[]
  archived: DraftRow[]
  error: ShareError | null
}

export type DraftAction =
  | { type: 'reset'; offers: DraftOffer[] }
  | { type: 'add'; offerId: number; name: string }
  | { type: 'archive'; offerId: number }
  | { type: 'restore'; offerId: number }
  | { type: 'togglePin'; offerId: number; currentShare: number }
  | { type: 'setShare'; offerId: number; share: number }

export function fromServer(offers: readonly CampaignOffer[]): DraftOffer[] {
  return offers.map((offer) => ({
    offerId: offer.offer_id,
    name: offer.name,
    share: offer.share,
    isPinned: offer.is_pinned,
    isArchived: offer.is_archived,
  }))
}

export function draftReducer(state: DraftOffer[], action: DraftAction): DraftOffer[] {
  switch (action.type) {
    case 'reset':
      return action.offers
    case 'add': {
      const existing = state.find((offer) => offer.offerId === action.offerId)
      if (existing)
        return existing.isArchived
          ? draftReducer(state, { type: 'restore', offerId: action.offerId })
          : state
      return [
        ...state,
        {
          offerId: action.offerId,
          name: action.name,
          share: 0,
          isPinned: false,
          isArchived: false,
        },
      ]
    }
    case 'archive':
      return update(state, action.offerId, { isArchived: true, isPinned: false })
    case 'restore':
      return update(state, action.offerId, { isArchived: false, isPinned: false })
    case 'togglePin': {
      const offer = state.find((item) => item.offerId === action.offerId)
      if (!offer) return state
      return update(
        state,
        action.offerId,
        offer.isPinned ? { isPinned: false } : { isPinned: true, share: action.currentShare },
      )
    }
    case 'setShare':
      return update(state, action.offerId, { isPinned: true, share: clampShare(action.share) })
  }
}

export function buildView(offers: readonly DraftOffer[]): DraftView {
  const activeOffers = offers.filter((offer) => !offer.isArchived)
  const allocation = allocateShares(
    activeOffers.map((offer) => ({ pinned: offer.isPinned, share: offer.share })),
  )
  const active = activeOffers.map((offer, index) => ({
    ...offer,
    effectiveShare: allocation.shares[index] ?? 0,
  }))
  const archived = offers
    .filter((offer) => offer.isArchived)
    .map((offer) => ({ ...offer, effectiveShare: null }))
  return { rows: [...active, ...archived], active, archived, error: allocation.error }
}

export function isDirty(view: DraftView, server: readonly CampaignOffer[]): boolean {
  return signature(view.rows) !== signature(buildView(fromServer(server)).rows)
}

export function toRequest(view: DraftView): CampaignOfferInput[] {
  return view.rows.map((row) => ({
    offer_id: row.offerId,
    share: row.effectiveShare ?? row.share,
    is_pinned: row.isPinned,
    is_archived: row.isArchived,
  }))
}

function signature(rows: readonly DraftRow[]): string {
  return JSON.stringify(
    rows.map((row) => [row.offerId, row.isArchived, row.isPinned, row.effectiveShare]),
  )
}

function update(state: DraftOffer[], offerId: number, patch: Partial<DraftOffer>): DraftOffer[] {
  return state.map((offer) => (offer.offerId === offerId ? { ...offer, ...patch } : offer))
}

function clampShare(share: number): number {
  if (!Number.isFinite(share)) return 0
  return Math.min(TOTAL_SHARE, Math.max(0, Math.round(share)))
}
