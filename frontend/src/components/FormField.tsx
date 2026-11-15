import { useId, type InputHTMLAttributes } from 'react'
import clsx from 'clsx'

interface FormFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string
  /** Validation message for this field, or null when the value is acceptable. */
  error?: string | null
  /** Guidance shown under the field when there is no error. */
  hint?: string
}

export function FormField({ label, error = null, hint, className, ...inputProps }: FormFieldProps) {
  const id = useId()
  const messageId = `${id}-message`
  const message = error ?? hint

  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        aria-invalid={error !== null}
        aria-describedby={message ? messageId : undefined}
        className={clsx(
          'block w-full rounded-lg border bg-obsidian px-3.5 py-2.5 text-sm text-content-primary placeholder:text-content-secondary/60',
          error !== null ? 'border-red-500/70' : 'border-card-border',
          className,
        )}
        {...inputProps}
      />
      {message && (
        <p
          id={messageId}
          className={clsx('mt-1.5 text-sm', error !== null ? 'text-red-300' : 'text-content-secondary')}
        >
          {message}
        </p>
      )}
    </div>
  )
}
