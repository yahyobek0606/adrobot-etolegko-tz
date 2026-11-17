import {
  buildView,
  draftReducer,
  fromServer,
  isDirty,
  toRequest,
  type DraftAction,
  type DraftOffer,
} from '@/features/campaign-editor/model/draft'
import type { CampaignOffer } from '@/lib/api/types'

const server: CampaignOffer[] = [
  { offer_id: 1, name: 'One', share: 25, is_pinned: true, is_archived: false },
  { offer_id: 2, name: 'Two', share: 25, is_pinned: true, is_archived: false },
  { offer_id: 3, name: 'Three', share: 25, is_pinned: false, is_archived: false },
  { offer_id: 4, name: 'Four', share: 25, is_pinned: false, is_archived: false },
  { offer_id: 5, name: 'Five', share: 10, is_pinned: false, is_archived: true },
]

function run(...actions: DraftAction[]): DraftOffer[] {
  return actions.reduce(draftReducer, fromServer(server))
}

const shares = (offers: DraftOffer[]) =>
  buildView(offers).rows.map((row) => [row.offerId, row.effectiveShare])

describe('draft', () => {
  it('matches the server and is clean before any change', () => {
    const view = buildView(run())

    expect(shares(run())).toEqual([
      [1, 25],
      [2, 25],
      [3, 25],
      [4, 25],
      [5, null],
    ])
    expect(isDirty(view, server)).toBe(false)
  })

  it('keeps pinned shares when an offer is added', () => {
    const offers = run({ type: 'add', offerId: 6, name: 'Six' })

    expect(shares(offers)).toEqual([
      [1, 25],
      [2, 25],
      [3, 17],
      [4, 17],
      [6, 16],
      [5, null],
    ])
    expect(isDirty(buildView(offers), server)).toBe(true)
  })

  it('keeps pinned shares when an offer is archived', () => {
    expect(shares(run({ type: 'archive', offerId: 3 }))).toEqual([
      [1, 25],
      [2, 25],
      [4, 50],
      [3, null],
      [5, null],
    ])
  })

  it('restores an archived offer unpinned, also when it is added again', () => {
    const restored = run({ type: 'add', offerId: 5, name: 'Five' })

    expect(restored.find((offer) => offer.offerId === 5)).toMatchObject({
      isArchived: false,
      isPinned: false,
    })
    expect(shares(restored)).toEqual([
      [1, 25],
      [2, 25],
      [3, 17],
      [4, 17],
      [5, 16],
    ])
  })

  it('pins the current share and unpins on second toggle', () => {
    const pinned = run({ type: 'togglePin', offerId: 3, currentShare: 25 })
    expect(pinned.find((offer) => offer.offerId === 3)).toMatchObject({ isPinned: true, share: 25 })

    const unpinned = draftReducer(pinned, { type: 'togglePin', offerId: 1, currentShare: 25 })
    expect(shares(unpinned).slice(0, 4)).toEqual([
      [1, 25],
      [2, 25],
      [3, 25],
      [4, 25],
    ])
  })

  it('pins a manually edited share and clamps it', () => {
    const offers = run({ type: 'setShare', offerId: 3, share: 40.4 })

    expect(shares(offers).slice(0, 4)).toEqual([
      [1, 25],
      [2, 25],
      [3, 40],
      [4, 10],
    ])
    expect(draftReducer(offers, { type: 'setShare', offerId: 4, share: 500 })[3]?.share).toBe(100)
  })

  it('reports invalid allocations', () => {
    expect(buildView(run({ type: 'setShare', offerId: 3, share: 60 })).error).toBe(
      'pinned_exceeds_total',
    )
  })

  it('becomes clean again when changes are undone', () => {
    const offers = run({ type: 'archive', offerId: 4 }, { type: 'restore', offerId: 4 })

    expect(isDirty(buildView(offers), server)).toBe(false)
  })

  it('serializes the request in display order with effective shares', () => {
    expect(toRequest(buildView(run({ type: 'archive', offerId: 3 })))).toEqual([
      { offer_id: 1, share: 25, is_pinned: true, is_archived: false },
      { offer_id: 2, share: 25, is_pinned: true, is_archived: false },
      { offer_id: 4, share: 50, is_pinned: false, is_archived: false },
      { offer_id: 3, share: 25, is_pinned: false, is_archived: true },
      { offer_id: 5, share: 10, is_pinned: false, is_archived: true },
    ])
  })
})
