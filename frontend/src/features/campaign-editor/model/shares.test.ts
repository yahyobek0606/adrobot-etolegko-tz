import cases from '@shared/share-cases.json'

import {
  allocateShares,
  type ShareAllocation,
  type ShareSlot,
} from '@/features/campaign-editor/model/shares'

interface ShareCase {
  name: string
  input: ShareSlot[]
  expected: ShareAllocation
}

describe('allocateShares', () => {
  it.each(cases as ShareCase[])('$name', ({ input, expected }) => {
    expect(allocateShares(input)).toEqual(expected)
  })

  it('always sums to the total for valid allocations', () => {
    for (let count = 1; count < 30; count++) {
      const { shares, error } = allocateShares(
        Array.from({ length: count }, () => ({ pinned: false, share: 0 })),
      )

      expect(error).toBeNull()
      expect(shares.reduce((sum, share) => sum + share, 0)).toBe(100)
      expect(Math.max(...shares) - Math.min(...shares)).toBeLessThanOrEqual(1)
    }
  })
})
