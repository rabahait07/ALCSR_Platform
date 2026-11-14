import { useEffect, useState } from 'react'
import clsx from 'clsx'
import {
  Archive,
  BookOpen,
  ClipboardList,
  FileText,
  ListChecks,
  Terminal,
  type LucideIcon,
} from 'lucide-react'

import { fetchHealth } from './lib/api'

type ApiStatus = 'checking' | 'online' | 'offline'

interface Section {
  title: string
  description: string
  icon: LucideIcon
}

const SECTIONS: Section[] = [
  {
    title: 'Worksheets',
    description: 'Topic-by-topic question sheets with matching answer PDFs.',
    icon: FileText,
  },
  {
    title: 'MCQs',
    description: 'Multiple-choice quizzes for every sub-topic, graded on the server.',
    icon: ListChecks,
  },
  {
    title: 'Notes',
    description: 'Learning notes for first study and reviewing notes for recall.',
    icon: BookOpen,
  },
  {
    title: 'Exam Questions',
    description: 'Exam question packs with mark schemes for each specification area.',
    icon: ClipboardList,
  },
  {
    title: 'Past Papers',
    description: 'Question papers, mark schemes and walkthroughs from 2017 onwards.',
    icon: Archive,
  },
  {
    title: 'Coding Challenges',
    description: 'Python challenges that run in your browser with Pyodide.',
    icon: Terminal,
  },
]

const STATUS_LABEL: Record<ApiStatus, string> = {
  checking: 'Checking API…',
  online: 'API online',
  offline: 'API offline',
}

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('checking')

  useEffect(() => {
    const controller = new AbortController()

    fetchHealth(controller.signal)
      .then((healthy) => setApiStatus(healthy ? 'online' : 'offline'))
      .catch(() => {
        if (!controller.signal.aborted) setApiStatus('offline')
      })

    return () => controller.abort()
  }, [])

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-card-border">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-xl font-bold tracking-tight">
            AL<span className="text-brand-light">CSR</span>
          </span>
          <span
            role="status"
            className="flex items-center gap-2 rounded-full border border-card-border bg-surface px-3 py-1 text-sm text-content-secondary"
          >
            <span
              aria-hidden="true"
              className={clsx('h-2 w-2 rounded-full', {
                'animate-pulse bg-content-secondary': apiStatus === 'checking',
                'bg-emerald-500': apiStatus === 'online',
                'bg-red-500': apiStatus === 'offline',
              })}
            />
            {STATUS_LABEL[apiStatus]}
          </span>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-16">
        <p className="text-sm font-semibold uppercase tracking-widest text-brand-light">
          OCR H446
        </p>
        <h1 className="mt-3 max-w-2xl text-4xl font-bold tracking-tight sm:text-5xl">
          A-Level Computer Science Revision
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-content-secondary">
          Everything for Paper 1 and Paper 2 in one place, organised by the specification.
        </p>

        <ul className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SECTIONS.map(({ title, description, icon: Icon }) => (
            <li key={title} className="rounded-xl border border-card-border bg-surface p-6">
              <span className="inline-flex rounded-lg bg-brand/10 p-2.5 text-brand-light">
                <Icon aria-hidden="true" className="h-5 w-5" />
              </span>
              <h2 className="mt-4 text-lg font-semibold">{title}</h2>
              <p className="mt-1 text-sm leading-relaxed text-content-secondary">{description}</p>
            </li>
          ))}
        </ul>
      </main>

      <footer className="border-t border-card-border py-6 text-center text-sm text-content-secondary">
        ALCSR · A-Level Computer Science Revision
      </footer>
    </div>
  )
}

export default App
