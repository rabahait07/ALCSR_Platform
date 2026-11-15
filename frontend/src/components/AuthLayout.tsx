import type { FormEvent, ReactNode } from 'react'

import { ErrorAlert } from './ErrorAlert'

interface AuthLayoutProps {
  title: string
  subtitle: string
  /** A problem with the whole form, such as wrong credentials; shown above the fields. */
  error: string | null
  submitLabel: string
  submittingLabel: string
  isSubmitting: boolean
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  /** The form fields. */
  children: ReactNode
  /** The line under the form that links to the other auth page. */
  footer: ReactNode
}

/** The centred card shared by the login and signup pages. */
export function AuthLayout({
  title,
  subtitle,
  error,
  submitLabel,
  submittingLabel,
  isSubmitting,
  onSubmit,
  children,
  footer,
}: AuthLayoutProps) {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <span className="inline-block rounded-md bg-brand px-2.5 py-1 text-base font-bold tracking-wide text-white">
            ALCSR
          </span>
          <p className="mt-4 text-content-secondary">
            You are one step away from a guaranteed A*
          </p>
        </div>

        <div className="rounded-2xl border border-card-border bg-surface p-6 sm:p-8">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1 text-sm text-content-secondary">{subtitle}</p>

          <form onSubmit={onSubmit} noValidate className="mt-6 space-y-5">
            {error !== null && <ErrorAlert message={error} />}
            {children}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-lg bg-brand px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-light disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? submittingLabel : submitLabel}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-sm text-content-secondary">{footer}</p>
      </div>
    </main>
  )
}
