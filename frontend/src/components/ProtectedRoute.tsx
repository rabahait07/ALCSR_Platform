import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { Spinner } from './Spinner'
import { useAuth } from '../hooks/useAuth'

/** Renders its child routes for a signed-in user and sends everyone else to /login. */
export function ProtectedRoute() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <Spinner fullPage label="Checking your session" />
  }
  if (user === null) {
    // Remember where the visitor was heading so login can return them there.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
