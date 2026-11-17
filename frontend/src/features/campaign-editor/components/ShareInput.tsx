import { useState } from 'react'

import { Input } from '@/components/ui/input'

interface ShareInputProps {
  value: number
  label: string
  onChange: (share: number) => void
}

export function ShareInput({ value, label, onChange }: ShareInputProps) {
  const [text, setText] = useState<string | null>(null)

  const update = (raw: string) => {
    const digits = raw.replace(/[^\d]/g, '').slice(0, 3)
    setText(digits)
    const share = Number.parseInt(digits, 10)
    if (!Number.isNaN(share) && share !== value) onChange(share)
  }

  return (
    <div className="relative w-24">
      <Input
        aria-label={label}
        inputMode="numeric"
        value={text ?? value.toString()}
        onChange={(event) => update(event.target.value)}
        onBlur={() => setText(null)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') setText(null)
        }}
        className="pr-7 text-right tabular-nums"
      />
      <span className="pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2 text-sm text-muted-foreground">
        %
      </span>
    </div>
  )
}
