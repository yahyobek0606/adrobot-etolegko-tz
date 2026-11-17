export const TOTAL_SHARE = 100

export type ShareError = 'no_active_offers' | 'pinned_exceeds_total' | 'pinned_total_mismatch'

export interface ShareSlot {
  pinned: boolean
  share: number
}

export interface ShareAllocation {
  shares: number[]
  error: ShareError | null
}

export function allocateShares(slots: readonly ShareSlot[]): ShareAllocation {
  if (slots.length === 0) return { shares: [], error: 'no_active_offers' }

  const pinnedTotal = slots.reduce((sum, slot) => (slot.pinned ? sum + slot.share : sum), 0)
  const unpinnedCount = slots.filter((slot) => !slot.pinned).length
  const remainder = TOTAL_SHARE - pinnedTotal

  if (remainder < 0) {
    return {
      shares: slots.map((slot) => (slot.pinned ? slot.share : 0)),
      error: 'pinned_exceeds_total',
    }
  }

  if (unpinnedCount === 0) {
    return {
      shares: slots.map((slot) => slot.share),
      error: remainder === 0 ? null : 'pinned_total_mismatch',
    }
  }

  const base = Math.floor(remainder / unpinnedCount)
  const leftover = remainder % unpinnedCount
  let unpinnedIndex = 0

  const shares = slots.map((slot) => {
    if (slot.pinned) return slot.share
    const share = base + (unpinnedIndex < leftover ? 1 : 0)
    unpinnedIndex += 1
    return share
  })

  return { shares, error: null }
}
