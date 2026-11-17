import { useEffect } from 'react'
import { useBlocker } from 'react-router'

import { ConfirmDialog } from '@/components/ConfirmDialog'

export function UnsavedChangesGuard({ when }: { when: boolean }) {
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      when && currentLocation.pathname !== nextLocation.pathname,
  )

  useEffect(() => {
    if (!when) return
    const warn = (event: BeforeUnloadEvent) => event.preventDefault()
    window.addEventListener('beforeunload', warn)
    return () => window.removeEventListener('beforeunload', warn)
  }, [when])

  return (
    <ConfirmDialog
      open={blocker.state === 'blocked'}
      title="Leave without pushing?"
      description="Your changes to this campaign have not been pushed to Keitaro and will be lost."
      confirmLabel="Discard and leave"
      onConfirm={() => blocker.proceed?.()}
      onCancel={() => blocker.reset?.()}
    />
  )
}
