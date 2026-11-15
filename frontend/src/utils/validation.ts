/**
 * Form validation mirroring the rules in backend/app/schemas/user.py, so that most mistakes
 * are caught before a request is sent. Each function returns a message, or null when valid.
 */

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const MIN_PASSWORD_LENGTH = 8
const MAX_PASSWORD_LENGTH = 128
// bcrypt only uses the first 72 bytes of a password, so the server rejects longer ones.
const MAX_PASSWORD_BYTES = 72
const MAX_NAME_LENGTH = 120

export function validateFullName(value: string): string | null {
  const name = value.trim()
  if (name.length === 0) {
    return 'Enter your full name.'
  }
  if (name.length > MAX_NAME_LENGTH) {
    return `Use ${MAX_NAME_LENGTH} characters or fewer.`
  }
  return null
}

export function validateEmail(value: string): string | null {
  const email = value.trim()
  if (email.length === 0) {
    return 'Enter your email address.'
  }
  if (!EMAIL_PATTERN.test(email)) {
    return 'Enter an email address in the format name@example.com.'
  }
  return null
}

/** For signup, where the password must meet the rules for new passwords. */
export function validateNewPassword(value: string): string | null {
  if (value.length === 0) {
    return 'Choose a password.'
  }
  if (value.length < MIN_PASSWORD_LENGTH) {
    return `Use at least ${MIN_PASSWORD_LENGTH} characters.`
  }
  if (
    value.length > MAX_PASSWORD_LENGTH ||
    new TextEncoder().encode(value).length > MAX_PASSWORD_BYTES
  ) {
    return 'That password is too long. Use a shorter one.'
  }
  return null
}

/** For login, where any non-empty password is sent for the server to check. */
export function validateExistingPassword(value: string): string | null {
  return value.length === 0 ? 'Enter your password.' : null
}
