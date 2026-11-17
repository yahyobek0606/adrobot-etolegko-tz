import { COUNTRY_CODES } from '@/lib/country-codes'

const displayNames = new Intl.DisplayNames(['en'], { type: 'region' })

export interface ParsedCountries {
  codes: string[]
  invalid: string[]
}

export function parseCountryCodes(input: string): ParsedCountries {
  const tokens = input
    .split(/[\s,;]+/)
    .map((token) => token.trim().toUpperCase())
    .filter(Boolean)
  const unique = [...new Set(tokens)]
  return {
    codes: unique.filter((code) => COUNTRY_CODES.has(code)),
    invalid: unique.filter((code) => !COUNTRY_CODES.has(code)),
  }
}

export function countryName(code: string): string {
  return displayNames.of(code) ?? code
}
