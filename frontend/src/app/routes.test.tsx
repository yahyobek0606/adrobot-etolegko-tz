import { screen } from '@testing-library/react'

import { renderRoute } from '@/test/render'

describe('routes', () => {
  it.each([
    ['/', 'Campaigns'],
    ['/campaigns/new', 'New campaign'],
    ['/campaigns/101', 'Test AU campaign'],
  ])('renders %s', async (path, heading) => {
    renderRoute(path)

    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
  })
})
