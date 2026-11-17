interface ErrorBody {
  detail?: unknown
  code?: string
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string | undefined

  constructor(status: number, message: string, code?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

function describe(detail: unknown): string | undefined {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: unknown) =>
        item && typeof item === 'object' && 'msg' in item ? String(item.msg) : undefined,
      )
      .filter(Boolean)
    return messages.length ? messages.join('; ') : undefined
  }
  return undefined
}

export async function unwrap<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await request
  if (error !== undefined || !response.ok) {
    const body = (error ?? {}) as ErrorBody
    const message =
      describe(body.detail) ?? `Request failed with status ${response.status.toString()}`
    throw new ApiError(response.status, message, body.code)
  }
  return data as T
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong'
}

export function isConflict(error: unknown): boolean {
  return error instanceof ApiError && error.status === 409
}
