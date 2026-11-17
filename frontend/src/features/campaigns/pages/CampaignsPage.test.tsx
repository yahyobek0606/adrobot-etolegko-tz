import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { renderRoute } from '@/test/render'

async function openCampaigns() {
  const user = userEvent.setup()
  renderRoute('/')
  await screen.findByRole('link', { name: 'Test AU campaign' })
  return user
}

describe('CampaignsPage', () => {
  it('shows campaigns from the default group and filters by search', async () => {
    const user = await openCampaigns()

    expect(screen.getByRole('link', { name: 'Test AU campaign' })).toHaveAttribute(
      'href',
      '/campaigns/101',
    )
    expect(await screen.findByText('1 of 2')).toBeInTheDocument()
    expect(screen.queryByText('Someone else')).not.toBeInTheDocument()

    await user.type(screen.getByLabelText('Search campaigns'), 'nothing like this')
    expect(screen.getByText(/No campaigns match/)).toBeInTheDocument()
  })

  it('has a view details button for each campaign', async () => {
    const user = await openCampaigns()
    const row = screen.getByRole('link', { name: 'Test AU campaign' }).closest('tr') as HTMLElement

    await user.click(within(row).getByRole('link', { name: 'View details of Test AU campaign' }))

    expect(await screen.findByRole('heading', { name: 'Test AU campaign' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Fetch streams from KT/ })).toBeInTheDocument()
  })

  it.each([['/'], ['{Control>}k{/Control}'], ['{Meta>}k{/Meta}']])(
    'focuses search with %s',
    async (keys) => {
      const user = await openCampaigns()

      await user.keyboard(keys)

      expect(screen.getByLabelText('Search campaigns')).toHaveFocus()
    },
  )

  it('clears and leaves search with Escape, then N opens a new campaign', async () => {
    const user = await openCampaigns()
    const search = screen.getByLabelText('Search campaigns')

    await user.keyboard('/')
    await user.keyboard('nothing')
    expect(search).toHaveValue('nothing')

    await user.keyboard('{Escape}')
    expect(search).toHaveValue('')
    expect(search).not.toHaveFocus()

    await user.keyboard('n')
    expect(await screen.findByRole('heading', { name: 'New campaign' })).toBeInTheDocument()
  })
})
