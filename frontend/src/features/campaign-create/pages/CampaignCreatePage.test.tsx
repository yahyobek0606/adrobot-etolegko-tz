import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'

import type { CampaignCreateRequest } from '@/lib/api/types'
import { campaigns } from '@/test/fixtures'
import { renderRoute } from '@/test/render'
import { server } from '@/test/server'

async function chooseOffer(user: ReturnType<typeof userEvent.setup>, search: string) {
  await user.click(screen.getByRole('combobox', { name: 'Offer for everyone else' }))
  await user.type(screen.getByPlaceholderText('Offer name or ID'), search)
  await user.click(await screen.findByRole('option', { name: /13972 Flexacil/ }))
}

describe('CampaignCreatePage', () => {
  it('creates a campaign and opens its editor', async () => {
    let received: CampaignCreateRequest | undefined
    server.use(
      http.post('*/api/v1/campaigns', async ({ request }) => {
        received = (await request.json()) as CampaignCreateRequest
        return HttpResponse.json(campaigns[0], { status: 201 })
      }),
    )
    const user = userEvent.setup()
    renderRoute('/campaigns/new')

    await user.type(await screen.findByLabelText('Campaign name'), '  Test AU campaign ')
    await user.type(screen.getByLabelText('Countries sent to Google'), 'au, mx')
    await chooseOffer(user, 'flex')

    const preview = screen.getByRole('region', { name: 'How visitors will be routed' })
    expect(within(preview).getByText('Visitors from Australia, Mexico')).toBeInTheDocument()
    expect(within(preview).getByText('google.com')).toBeInTheDocument()
    expect(within(preview).getByText('100%')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Create campaign' }))

    await waitFor(() =>
      expect(received).toEqual({
        name: 'Test AU campaign',
        countries: ['AU', 'MX'],
        offer_id: 13972,
        domain_id: 1813,
        group_id: 10332,
        traffic_source_id: 836,
      }),
    )
    expect(await screen.findByRole('heading', { name: 'Test AU campaign' })).toBeInTheDocument()
  })

  it('shows validation errors instead of submitting', async () => {
    const user = userEvent.setup()
    renderRoute('/campaigns/new')

    await user.type(await screen.findByLabelText('Countries sent to Google'), 'AU, XX')
    await user.click(screen.getByRole('button', { name: 'Create campaign' }))

    expect(await screen.findByText('Enter a campaign name')).toBeInTheDocument()
    expect(screen.getByText(/Not a country code: XX/)).toBeInTheDocument()
    expect(screen.getByText('Choose an offer')).toBeInTheDocument()
  })

  it('keeps the form and reports the error when Keitaro fails', async () => {
    server.use(
      http.post('*/api/v1/campaigns', () =>
        HttpResponse.json(
          { detail: 'Keitaro responded with 500 for POST /campaigns', code: 'provider_error' },
          { status: 502 },
        ),
      ),
    )
    const user = userEvent.setup()
    renderRoute('/campaigns/new')

    await user.type(await screen.findByLabelText('Campaign name'), 'Broken')
    await user.type(screen.getByLabelText('Countries sent to Google'), 'AU')
    await chooseOffer(user, '13972')
    await user.click(screen.getByRole('button', { name: 'Create campaign' }))

    expect(await screen.findByText('Campaign was not created')).toBeInTheDocument()
    expect(screen.getByText(/Keitaro responded with 500/)).toBeInTheDocument()
    expect(screen.getByLabelText('Campaign name')).toHaveValue('Broken')
  })
})
