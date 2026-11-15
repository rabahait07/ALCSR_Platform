import { Link } from 'react-router-dom'

import { PageHeader } from '../components/PageHeader'

export function NotFoundPage() {
  return (
    <>
      <PageHeader title="Page not found" description="There is nothing at this address." />
      <Link
        to="/dashboard"
        className="inline-block rounded-lg bg-brand px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-light"
      >
        Go to your dashboard
      </Link>
    </>
  )
}
