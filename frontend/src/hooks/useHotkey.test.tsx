import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { useHotkey, type Hotkey } from '@/hooks/useHotkey'

interface HarnessProps {
  hotkeys: Hotkey[]
  onHit: () => void
  withDialog?: boolean
}

function Harness({ hotkeys, onHit, withDialog = false }: HarnessProps) {
  useHotkey(hotkeys, onHit)
  return (
    <>
      <input aria-label="field" />
      {withDialog && <div role="dialog" />}
    </>
  )
}

function setup(hotkeys: Hotkey[], withDialog = false) {
  const calls: string[] = []
  const user = userEvent.setup()
  const view = render(
    <Harness hotkeys={hotkeys} withDialog={withDialog} onHit={() => calls.push('hit')} />,
  )
  return { user, calls, view }
}

describe('useHotkey', () => {
  it('fires on the plain key outside inputs only', async () => {
    const { user, calls, view } = setup([{ key: 'n' }])

    await user.keyboard('n')
    expect(calls).toHaveLength(1)

    await user.click(view.getByLabelText('field'))
    await user.keyboard('n')
    expect(calls).toHaveLength(1)
  })

  it('ignores the plain key when a modifier is held', async () => {
    const { user, calls } = setup([{ key: 'n' }])

    await user.keyboard('{Control>}n{/Control}')

    expect(calls).toHaveLength(0)
  })

  it('fires mod shortcuts even while typing', async () => {
    const { user, calls, view } = setup([{ key: 'k', mod: true }])

    await user.click(view.getByLabelText('field'))
    await user.keyboard('{Meta>}k{/Meta}')

    expect(calls).toHaveLength(1)
  })

  it('does nothing while a dialog is open', async () => {
    const { user, calls } = setup([{ key: 'n' }], true)

    await user.keyboard('n')

    expect(calls).toHaveLength(0)
  })
})
