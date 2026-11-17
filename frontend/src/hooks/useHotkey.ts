import { useEffect, useRef } from 'react'

export interface Hotkey {
  key: string
  mod?: boolean
}

interface HotkeyOptions {
  enabled?: boolean
  allowInInputs?: boolean
}

const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform)

export const modKeyLabel = isMac ? '⌘' : 'Ctrl'

function isEditable(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  return (
    target.isContentEditable ||
    target instanceof HTMLInputElement ||
    target instanceof HTMLTextAreaElement ||
    target instanceof HTMLSelectElement
  )
}

export function matchesHotkey(event: KeyboardEvent, hotkey: Hotkey): boolean {
  const mod = event.metaKey || event.ctrlKey
  if (Boolean(hotkey.mod) !== mod || event.altKey) return false
  return event.key.toLowerCase() === hotkey.key.toLowerCase()
}

export function useHotkey(
  hotkeys: Hotkey | Hotkey[],
  handler: (event: KeyboardEvent) => void,
  { enabled = true, allowInInputs = false }: HotkeyOptions = {},
) {
  const handlerRef = useRef(handler)
  useEffect(() => {
    handlerRef.current = handler
  })

  const serialized = JSON.stringify(Array.isArray(hotkeys) ? hotkeys : [hotkeys])

  useEffect(() => {
    if (!enabled) return
    const parsed = JSON.parse(serialized) as Hotkey[]
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.repeat) return
      const hit = parsed.find((hotkey) => matchesHotkey(event, hotkey))
      if (!hit) return
      if (!hit.mod && !allowInInputs && isEditable(event.target)) return
      if (document.querySelector('[role="dialog"], [role="alertdialog"]')) return
      event.preventDefault()
      handlerRef.current(event)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [serialized, enabled, allowInInputs])
}
