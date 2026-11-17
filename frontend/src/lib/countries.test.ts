import { countryName, parseCountryCodes } from '@/lib/countries'

describe('parseCountryCodes', () => {
  it('normalizes, de-duplicates and splits on commas or spaces', () => {
    expect(parseCountryCodes(' au, mx RO;AU ')).toEqual({ codes: ['AU', 'MX', 'RO'], invalid: [] })
  })

  it('reports codes that are not ISO alpha-2 countries', () => {
    expect(parseCountryCodes('AU, AUS, ZZ, 1')).toEqual({
      codes: ['AU'],
      invalid: ['AUS', 'ZZ', '1'],
    })
  })

  it('returns nothing for empty input', () => {
    expect(parseCountryCodes('  ')).toEqual({ codes: [], invalid: [] })
  })
})

describe('countryName', () => {
  it('resolves English names', () => {
    expect(countryName('AU')).toBe('Australia')
  })
})
