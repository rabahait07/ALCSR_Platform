import { useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

import { AuthLayout } from '../components/AuthLayout'
import { FormField } from '../components/FormField'
import { Spinner } from '../components/Spinner'
import { useAuth } from '../hooks/useAuth'
import { getErrorMessage } from '../services/api'
import { validateEmail, validateExistingPassword } from '../utils/validation'

interface FieldErrors {
  email: string | null
  password: string | null
}

const NO_ERRORS: FieldErrors = { email: null, password: null }
const LINK_CLASSES = 'rounded font-medium text-brand-light underline-offset-2 hover:underline'

/** Where to go after logging in: the page the visitor was sent here from, or the dashboard. */
function useReturnPath(): string {
  const { state } = useLocation()
  const from = (state as { from?: unknown } | null)?.from
  return typeof from === 'string' && from.startsWith('/') ? from : '/dashboard'
}

export function LoginPage() {
  const { user, isLoading, login } = useAuth()
  const navigate = useNavigate()
  const returnPath = useReturnPath()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>(NO_ERRORS)
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isLoading) {
    return <Spinner fullPage label="Checking your session" />
  }
  if (user !== null) {
    return <Navigate to={returnPath} replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const errors: FieldErrors = {
      email: validateEmail(email),
      password: validateExistingPassword(password),
    }
    setFieldErrors(errors)
    setFormError(null)
    if (errors.email !== null || errors.password !== null) {
      return
    }

    setIsSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate(returnPath, { replace: true })
    } catch (error) {
      setFormError(getErrorMessage(error, 'Could not log in. Try again.'))
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Log in"
      subtitle="Log in to your computer science portal"
      error={formError}
      submitLabel="Log in"
      submittingLabel="Logging in…"
      isSubmitting={isSubmitting}
      onSubmit={handleSubmit}
      footer={
        <>
          New to ALCSR?{' '}
          <Link to="/signup" className={LINK_CLASSES}>
            Sign up
          </Link>
        </>
      }
    >
      <FormField
        label="Email address"
        type="email"
        name="email"
        autoComplete="email"
        placeholder="student@alcsr.edu"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        error={fieldErrors.email}
      />
      <FormField
        label="Password"
        type="password"
        name="password"
        autoComplete="current-password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        error={fieldErrors.password}
      />
    </AuthLayout>
  )
}
