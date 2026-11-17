import { zodResolver } from '@hookform/resolvers/zod'
import { LoaderCircleIcon } from 'lucide-react'
import { useEffect } from 'react'
import { Controller, useForm, useWatch } from 'react-hook-form'

import { Button } from '@/components/ui/button'
import { Field, FieldDescription, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { RoutingPreview } from '@/features/campaign-create/components/RoutingPreview'
import {
  campaignCreateSchema,
  emptyCampaignCreateValues,
  toCreateRequest,
  type CampaignCreateValues,
} from '@/features/campaign-create/model/schema'
import { OfferCombobox } from '@/features/offers/components/OfferCombobox'
import type { CampaignCreateRequest, CampaignFormOptions, NamedRef } from '@/lib/api/types'
import { countryName, parseCountryCodes } from '@/lib/countries'

interface CampaignCreateFormProps {
  options: CampaignFormOptions
  isSubmitting: boolean
  onSubmit: (request: CampaignCreateRequest) => void
}

export function CampaignCreateForm({ options, isSubmitting, onSubmit }: CampaignCreateFormProps) {
  const form = useForm<CampaignCreateValues>({
    resolver: zodResolver(campaignCreateSchema),
    defaultValues: emptyCampaignCreateValues,
    mode: 'onTouched',
  })

  useEffect(() => {
    form.reset({
      ...emptyCampaignCreateValues,
      domainId: String(options.defaults.domain_id),
      groupId: String(options.defaults.group_id),
      trafficSourceId: String(options.defaults.traffic_source_id),
    })
    form.setFocus('name')
  }, [form, options.defaults])

  const [geo, offer] = useWatch({ control: form.control, name: ['geo', 'offer'] })
  const countries = parseCountryCodes(geo).codes

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)] lg:gap-8">
      <form
        noValidate
        onSubmit={form.handleSubmit((values) => onSubmit(toCreateRequest(values)))}
        className="rounded-xl bg-card p-6 shadow-xs"
      >
        <FieldGroup>
          <Controller
            name="name"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="campaign-name">Campaign name</FieldLabel>
                <Input
                  {...field}
                  id="campaign-name"
                  autoComplete="off"
                  placeholder="e.g. Flexacil PE test"
                  aria-invalid={fieldState.invalid}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />

          <Controller
            name="geo"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="campaign-geo">Countries sent to Google</FieldLabel>
                <Input
                  {...field}
                  id="campaign-geo"
                  autoComplete="off"
                  placeholder="AU, MX, RO"
                  aria-invalid={fieldState.invalid}
                  className="uppercase placeholder:normal-case"
                />
                {fieldState.invalid ? (
                  <FieldError errors={[fieldState.error]} />
                ) : (
                  <FieldDescription>
                    {countries.length > 0
                      ? countries.map(countryName).join(', ')
                      : 'Two-letter country codes, separated by commas.'}
                  </FieldDescription>
                )}
              </Field>
            )}
          />

          <Controller
            name="offer"
            control={form.control}
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="campaign-offer">Offer for everyone else</FieldLabel>
                <OfferCombobox
                  id="campaign-offer"
                  value={field.value}
                  onChange={(selected) => {
                    field.onChange(selected)
                    field.onBlur()
                  }}
                  invalid={fieldState.invalid}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />

          <RefSelect form={form} name="domainId" label="Domain" options={options.domains} />
          <div className="grid gap-6 sm:grid-cols-2">
            <RefSelect form={form} name="groupId" label="Group" options={options.groups} />
            <RefSelect
              form={form}
              name="trafficSourceId"
              label="Traffic source"
              options={options.traffic_sources}
            />
          </div>

          <Button type="submit" size="lg" disabled={isSubmitting} className="w-full">
            {isSubmitting && <LoaderCircleIcon className="animate-spin" />}
            {isSubmitting ? 'Creating campaign' : 'Create campaign'}
          </Button>
        </FieldGroup>
      </form>

      <div className="lg:sticky lg:top-6">
        <RoutingPreview
          countries={countries}
          offer={offer}
          redirectUrl={options.fallback_redirect_url}
        />
      </div>
    </div>
  )
}

interface RefSelectProps {
  form: ReturnType<typeof useForm<CampaignCreateValues>>
  name: 'domainId' | 'groupId' | 'trafficSourceId'
  label: string
  options: NamedRef[]
}

function RefSelect({ form, name, label, options }: RefSelectProps) {
  const id = `campaign-${name}`
  return (
    <Controller
      name={name}
      control={form.control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid}>
          <FieldLabel htmlFor={id}>{label}</FieldLabel>
          <Select value={field.value} onValueChange={field.onChange}>
            <SelectTrigger id={id} aria-invalid={fieldState.invalid} className="w-full bg-card">
              <SelectValue placeholder={`Choose ${label.toLowerCase()}`} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.id} value={String(option.id)}>
                  {option.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <FieldError errors={[fieldState.error]} />
        </Field>
      )}
    />
  )
}
