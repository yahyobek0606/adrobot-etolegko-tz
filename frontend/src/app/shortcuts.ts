import type { Hotkey } from '@/hooks/useHotkey'

export const shortcuts = {
  newCampaign: [{ key: 'n' }] satisfies Hotkey[],
  search: [{ key: '/' }, { key: 'k', mod: true }] satisfies Hotkey[],
  pushChanges: [{ key: 's', mod: true }] satisfies Hotkey[],
  fetchFromKeitaro: [{ key: 'f' }] satisfies Hotkey[],
  viewInKeitaro: [{ key: 'v' }] satisfies Hotkey[],
} as const
