import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { vi } from 'vitest'

import type { CampaignOffersState, CampaignOffersUpdate } from '@/lib/api/types'
import { campaignOffers } from '@/test/fixtures'
import { renderRoute } from '@/test/render'
import { server } from '@/test/server'

function rowFor(name: RegExp) {
  return screen.getByText(name).closest('tr') as HTMLElement
}

async function openEditor() {
  const user = userEvent.setup()
  renderRoute('/campaigns/101')
  expect(await screen.findByRole('heading', { name: 'Test AU campaign' })).toBeInTheDocument()
  return user
}

describe('CampaignEditorPage', () => {
  it('shows offers, shares and archived rows in sync', async () => {
    await openEditor()

    expect(screen.getByLabelText('Share for 13972 Flexacil [JOINT-PE]')).toHaveValue('50')
    expect(screen.getByLabelText('Share for 24800 Flexacil [land es]')).toHaveValue('50')
    expect(within(rowFor(/16361 Old offer/)).getByRole('button', { name: /Restore/ })).toBeVisible()
    expect(screen.getByText('In sync with Keitaro')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Push changes/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled()
    expect(screen.getByRole('link', { name: /View in KT/ })).toHaveAttribute(
      'href',
      campaignOffers.campaign.admin_url,
    )
  })

  it('archives, restores and pushes the draft', async () => {
    let pushed: CampaignOffersUpdate | undefined
    server.use(
      http.put('*/api/v1/campaigns/:campaignId/offers', async ({ request }) => {
        pushed = (await request.json()) as CampaignOffersUpdate
        const result: CampaignOffersState = {
          ...campaignOffers,
          offers: pushed.offers.map((offer, index) => ({
            ...offer,
            name: campaignOffers.offers[index]?.name ?? 'x',
          })),
        }
        return HttpResponse.json(result)
      }),
    )
    const user = await openEditor()

    await user.click(within(rowFor(/16361 Old offer/)).getByRole('button', { name: /Restore/ }))
    expect(screen.getByText('Unsaved changes')).toBeInTheDocument()
    expect(screen.getByLabelText('Share for 16361 Old offer')).toHaveValue('25')

    await user.click(screen.getByRole('button', { name: 'Delete 24800 Flexacil [land es]' }))
    expect(within(rowFor(/24800 Flexacil/)).getByText('Archived')).toBeInTheDocument()
    expect(screen.getByLabelText('Share for 16361 Old offer')).toHaveValue('50')

    await user.click(screen.getByRole('button', { name: /Push changes/ }))

    await waitFor(() =>
      expect(pushed).toEqual({
        offers: [
          { offer_id: 13972, share: 50, is_pinned: true, is_archived: false },
          { offer_id: 16361, share: 50, is_pinned: false, is_archived: false },
          { offer_id: 24800, share: 50, is_pinned: false, is_archived: true },
        ],
        revision: campaignOffers.revision,
      }),
    )
    expect(await screen.findByText('Changes pushed to Keitaro')).toBeInTheDocument()
  })

  it('offers to fetch when Keitaro changed since the page was loaded', async () => {
    server.use(
      http.put('*/api/v1/campaigns/:campaignId/offers', () =>
        HttpResponse.json(
          { detail: 'Offers in Keitaro changed after this page was loaded', code: 'conflict' },
          { status: 409 },
        ),
      ),
    )
    const user = await openEditor()

    await user.click(screen.getByRole('button', { name: 'Delete 24800 Flexacil [land es]' }))
    await user.click(
      screen.getByRole('button', { name: 'Unpin share for 13972 Flexacil [JOINT-PE]' }),
    )
    await user.click(screen.getByRole('button', { name: /Push changes/ }))
    await user.click(await screen.findByRole('button', { name: 'Fetch from KT' }))

    expect(await screen.findByRole('alertdialog')).toHaveTextContent(/Discard changes/)
  })

  it('pins a typed share and blocks pushing invalid totals', async () => {
    const user = await openEditor()
    const share = screen.getByLabelText('Share for 24800 Flexacil [land es]')

    await user.clear(share)
    await user.type(share, '70{Enter}')

    expect(
      screen.getByRole('button', { name: 'Unpin share for 24800 Flexacil [land es]' }),
    ).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText(/Pinned shares add up to more than 100%/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Push changes/ })).toBeDisabled()

    await user.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.getByText('In sync with Keitaro')).toBeInTheDocument()
  })

  it('adds an offer through the search dialog', async () => {
    const user = await openEditor()

    await user.click(screen.getByRole('button', { name: /Add offer/ }))
    const dialog = await screen.findByRole('dialog', { name: 'Add offer' })
    await user.click(within(dialog).getByRole('combobox'))
    await user.type(screen.getByPlaceholderText('Offer name or ID'), 'Miaflow')
    await user.click(await screen.findByRole('option', { name: /3749 Miaflow/ }))

    expect(screen.getByLabelText('Share for 3749 Miaflow [BEAUTY-RO]')).toHaveValue('25')
    expect(screen.getByLabelText('Share for 13972 Flexacil [JOINT-PE]')).toHaveValue('50')
  })

  it('blocks pushing when only pinned offers remain and they do not add up', async () => {
    const user = await openEditor()

    await user.click(screen.getByRole('button', { name: 'Delete 24800 Flexacil [land es]' }))

    expect(screen.getByText(/must add up to exactly 100%/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Push changes/ })).toBeDisabled()
  })

  it('asks before fetching from Keitaro over unpushed changes', async () => {
    let synced = false
    server.use(
      http.post('*/api/v1/campaigns/:campaignId/offers/sync', () => {
        synced = true
        return HttpResponse.json(campaignOffers)
      }),
    )
    const user = await openEditor()

    await user.click(screen.getByRole('button', { name: 'Delete 24800 Flexacil [land es]' }))
    await user.click(screen.getByRole('button', { name: /Fetch streams from KT/ }))
    const confirm = await screen.findByRole('alertdialog')
    await user.click(within(confirm).getByRole('button', { name: 'Discard and fetch' }))

    await waitFor(() => expect(synced).toBe(true))
    expect(await screen.findByText('In sync with Keitaro')).toBeInTheDocument()
  })

  describe('keyboard shortcuts', () => {
    it('pushes with mod+S, including a share still being typed', async () => {
      let pushed: CampaignOffersUpdate | undefined
      server.use(
        http.put('*/api/v1/campaigns/:campaignId/offers', async ({ request }) => {
          pushed = (await request.json()) as CampaignOffersUpdate
          return HttpResponse.json(campaignOffers)
        }),
      )
      const user = await openEditor()
      const share = screen.getByLabelText('Share for 13972 Flexacil [JOINT-PE]')

      await user.clear(share)
      await user.type(share, '40')
      await user.keyboard('{Control>}s{/Control}')

      await waitFor(() =>
        expect(pushed?.offers.map((offer) => [offer.offer_id, offer.share])).toEqual([
          [13972, 40],
          [24800, 60],
          [16361, 20],
        ]),
      )
    })

    it('does nothing on mod+S without changes', async () => {
      let called = false
      server.use(
        http.put('*/api/v1/campaigns/:campaignId/offers', () => {
          called = true
          return HttpResponse.json(campaignOffers)
        }),
      )
      const user = await openEditor()

      await user.keyboard('{Meta>}s{/Meta}')

      await new Promise((resolve) => setTimeout(resolve, 50))
      expect(called).toBe(false)
    })

    it('fetches with F and asks first when there are changes', async () => {
      let syncs = 0
      server.use(
        http.post('*/api/v1/campaigns/:campaignId/offers/sync', () => {
          syncs += 1
          return HttpResponse.json(campaignOffers)
        }),
      )
      const user = await openEditor()

      await user.keyboard('f')
      await waitFor(() => expect(syncs).toBe(1))

      await user.click(within(rowFor(/16361 Old offer/)).getByRole('button', { name: /Restore/ }))
      await user.keyboard('f')
      expect(await screen.findByRole('alertdialog')).toBeInTheDocument()
      expect(syncs).toBe(1)
    })

    it('opens the campaign in Keitaro with V', async () => {
      const open = vi.spyOn(window, 'open').mockReturnValue(null)
      const user = await openEditor()

      await user.keyboard('v')

      expect(open).toHaveBeenCalledWith(
        campaignOffers.campaign.admin_url,
        '_blank',
        'noopener,noreferrer',
      )
      open.mockRestore()
    })
  })
})
