import { Outlet } from 'react-router-dom'

import { Navbar } from './Navbar'

/** The frame around every signed-in page: the navigation bar above the page content. */
export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-10 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}
