import clsx from 'clsx'

interface SpinnerProps {
  /** Announced to screen readers and shown beside the spinner. */
  label: string
  /** Centre the spinner in the whole viewport instead of in its container. */
  fullPage?: boolean
}

export function Spinner({ label, fullPage = false }: SpinnerProps) {
  return (
    <div
      role="status"
      className={clsx(
        'flex items-center justify-center gap-3 text-sm text-content-secondary',
        fullPage ? 'min-h-screen bg-obsidian' : 'py-16',
      )}
    >
      <span
        aria-hidden="true"
        className="h-5 w-5 animate-spin rounded-full border-2 border-card-border border-t-brand-light motion-reduce:animate-none"
      />
      {label}
    </div>
  )
}
