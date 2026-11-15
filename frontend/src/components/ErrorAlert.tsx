import { CircleAlert } from 'lucide-react'

interface ErrorAlertProps {
  message: string
  /** When given, a "Try again" button is shown that calls this. */
  onRetry?: () => void
}

export function ErrorAlert({ message, onRetry }: ErrorAlertProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200"
    >
      <CircleAlert aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
      <p className="flex-1">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 rounded font-medium text-red-100 underline underline-offset-2 hover:text-white"
        >
          Try again
        </button>
      )}
    </div>
  )
}
