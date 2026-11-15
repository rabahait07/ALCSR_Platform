import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { AuthLayout } from '../components/AuthLayout'
import { FormField } from '../components/FormField'
import { Spinner } from '../components/Spinner'
import { useAuth } from '../hooks/useAuth'
import { getErrorMessage } from '../services/api'
import { validateEmail, validateFullName, validateNewPassword } from '../utils/validation'

interface FieldErrors {
  fullName: string | null
  email: string | null
  password: string | null
}

const NO_ERRORS: FieldErrors = { fullName: null, email: null, password: null }
const LINK_CLASSES = 'rounded font-medium text-brand-light underline-offset-2 hover:underline'

export function SignupPage() {
  const { user, isLoading, signup } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>(NO_ERRORS)
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isLoading) {
    return <Spinner fullPage label="Checking your session" />
  }
  if (user !== null) {
    return <Navigate to="/dashboard" replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const errors: FieldErrors = {
      fullName: validateFullName(fullName),
      email: validateEmail(email),
      password: validateNewPassword(password),
    }
    setFieldErrors(errors)
    setFormError(null)
    if (Object.values(errors).some((message) => message !== null)) {
      return
    }

    setIsSubmitting(true)
    try {
      await signup(fullName.trim(), email.trim(), password)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setFormError(getErrorMessage(error, 'Could not create your account. Try again.'))
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Sign up"
      subtitle="Sign up for your computer science portal"
      error={formError}
      submitLabel="Sign up"
      submittingLabel="Creating your account…"
      isSubmitting={isSubmitting}
      onSubmit={handleSubmit}
      footer={
        <>
          Already have an account?{' '}
          <Link to="/login" className={LINK_CLASSES}>
            Log in
          </Link>
        </>
      }
    >
      <FormField
        label="Full name"
        type="text"
        name="name"
        autoComplete="name"
        value={fullName}
        onChange={(event) => setFullName(event.target.value)}
        error={fieldErrors.fullName}
      />
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
        name="new-password"
        autoComplete="new-password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        error={fieldErrors.password}
        hint="At least 8 characters."
      />
    </AuthLayout>
  )
}
