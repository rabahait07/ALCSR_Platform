import clsx from 'clsx'
import { Check } from 'lucide-react'
import { Link } from 'react-router-dom'

import { ErrorAlert } from '../components/ErrorAlert'
import { PageHeader } from '../components/PageHeader'
import { Spinner } from '../components/Spinner'
import { useFetch } from '../hooks/useFetch'
import type { CodingChallengeSummary, Difficulty } from '../types'

const DIFFICULTY_CLASSES: Record<Difficulty, string> = {
  Easy: 'bg-emerald-500/15 text-emerald-300',
  Medium: 'bg-amber-500/15 text-amber-300',
  Hard: 'bg-red-500/15 text-red-300',
}

function attemptsLabel(challenge: CodingChallengeSummary): string {
  if (challenge.attempts_count === 0) {
    return 'Not attempted'
  }
  return challenge.attempts_count === 1 ? '1 attempt' : `${challenge.attempts_count} attempts`
}

export function ChallengesPage() {
  const { data, error, isLoading, reload } = useFetch<CodingChallengeSummary[]>('/challenges')

  return (
    <>
      <PageHeader
        title="OCR Computer Science Coding Challenges"
        description="Programming challenges tailored to the A Level Computer Science specification."
      />
      {isLoading && <Spinner label="Loading challenges" />}
      {error !== null && <ErrorAlert message={error} onRetry={reload} />}
      {data !== null && data.length === 0 && (
        <p className="text-sm text-content-secondary">No challenges are available yet.</p>
      )}
      {data !== null && data.length > 0 && (
        <ul className="max-w-3xl divide-y divide-card-border overflow-hidden rounded-lg border border-card-border bg-surface">
          {data.map((challenge) => (
            <li key={challenge.slug}>
              <Link
                to={`/challenges/${challenge.slug}`}
                className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-4 transition-colors hover:bg-obsidian focus-visible:bg-obsidian"
              >
                <span className="flex-1 font-medium">{challenge.title}</span>
                <span className="text-sm text-content-secondary">{attemptsLabel(challenge)}</span>
                {challenge.solved && (
                  <span className="flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-300">
                    <Check aria-hidden="true" className="h-3 w-3" />
                    Solved
                  </span>
                )}
                <span
                  className={clsx(
                    'rounded-full px-2 py-0.5 text-xs font-medium',
                    DIFFICULTY_CLASSES[challenge.difficulty],
                  )}
                >
                  {challenge.difficulty}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}
