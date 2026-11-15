import { useState } from 'react'
import clsx from 'clsx'
import { LogOut, Menu, X } from 'lucide-react'
import { Link, NavLink } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/worksheets', label: 'Worksheets' },
  { to: '/notes', label: 'Notes' },
  { to: '/exam-questions', label: 'Exam Questions' },
  { to: '/past-papers', label: 'Past Papers' },
  { to: '/mcqs', label: 'MCQs' },
  { to: '/challenges', label: 'Coding Challenges' },
] as const

const MOBILE_MENU_ID = 'primary-navigation-menu'

export function Navbar() {
  const { user, logout } = useAuth()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const closeMenu = () => setIsMenuOpen(false)

  return (
    <header className="sticky top-0 z-40 border-b border-card-border bg-surface">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6">
        <Link
          to="/dashboard"
          onClick={closeMenu}
          aria-label="ALCSR home"
          className="rounded-md bg-brand px-2.5 py-1 text-base font-bold tracking-wide text-white"
        >
          ALCSR
        </Link>

        <nav aria-label="Primary" className="hidden h-full flex-1 items-stretch gap-1 xl:flex">
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  // The bottom border sits on the header's own border to mark the current page.
                  '-mb-px flex items-center whitespace-nowrap border-b-2 px-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-brand-light text-content-primary'
                    : 'border-transparent text-content-secondary hover:text-content-primary',
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto hidden items-center gap-3 xl:flex">
          {user && (
            <span
              title={user.email}
              className="max-w-[12rem] truncate rounded-full border border-card-border bg-obsidian px-3 py-1 text-sm text-content-primary"
            >
              {user.full_name}
            </span>
          )}
          <button
            type="button"
            onClick={logout}
            className="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium text-content-secondary transition-colors hover:bg-obsidian hover:text-content-primary"
          >
            <LogOut aria-hidden="true" className="h-4 w-4" />
            Log out
          </button>
        </div>

        <button
          type="button"
          onClick={() => setIsMenuOpen((open) => !open)}
          aria-expanded={isMenuOpen}
          aria-controls={MOBILE_MENU_ID}
          aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
          className="ml-auto rounded-md p-2 text-content-secondary transition-colors hover:bg-obsidian hover:text-content-primary xl:hidden"
        >
          {isMenuOpen ? (
            <X aria-hidden="true" className="h-5 w-5" />
          ) : (
            <Menu aria-hidden="true" className="h-5 w-5" />
          )}
        </button>
      </div>

      {isMenuOpen && (
        <div id={MOBILE_MENU_ID} className="border-t border-card-border xl:hidden">
          <nav aria-label="Primary" className="mx-auto flex max-w-7xl flex-col px-4 py-2 sm:px-6">
            {NAV_LINKS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={closeMenu}
                className={({ isActive }) =>
                  clsx(
                    'rounded-md px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-obsidian text-content-primary'
                      : 'text-content-secondary hover:bg-obsidian hover:text-content-primary',
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 border-t border-card-border px-4 py-3 sm:px-6">
            {user && (
              <span className="min-w-0 truncate px-3 text-sm text-content-primary">
                {user.full_name}
              </span>
            )}
            <button
              type="button"
              onClick={logout}
              className="flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-content-secondary transition-colors hover:bg-obsidian hover:text-content-primary"
            >
              <LogOut aria-hidden="true" className="h-4 w-4" />
              Log out
            </button>
          </div>
        </div>
      )}
    </header>
  )
}
