import type { ShareError } from '@/features/campaign-editor/model/shares'

export const shareErrorMessages: Record<ShareError, string> = {
  no_active_offers: 'Add or restore at least one offer before pushing.',
  pinned_exceeds_total:
    'Pinned shares add up to more than 100%. Unpin an offer or lower a pinned share.',
  pinned_total_mismatch:
    'Every offer is pinned, so the shares must add up to exactly 100%. Unpin one to balance automatically.',
}
