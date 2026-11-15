import { Link } from 'react-router-dom'

import { ErrorAlert } from '../components/ErrorAlert'
import { PageHeader } from '../components/PageHeader'
import { Spinner } from '../components/Spinner'
import { useAuth } from '../hooks/useAuth'
import { useFetch } from '../hooks/useFetch'
import type { DashboardMetrics, PaperProgress, RecentActivity } from '../types'

const DATE_FORMAT = new Intl.DateTimeFormat(undefined, {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
})

const LINK_CLASSES = 'rounded font-medium text-brand-light underline-offset-2 hover:underline'

interface StatProps {
  label: string
  value: string
  detail: string
}

function Stat({ label, value, detail }: StatProps) {
  return (
    <div className="rounded-lg border border-card-border bg-surface p-5">
      <dt className="text-sm text-content-secondary">{label}</dt>
      <dd className="mt-2 text-3xl font-semibold tabular-nums">{value}</dd>
      <dd className="mt-1 text-sm text-content-secondary">{detail}</dd>
    </div>
  )
}

function PaperProgressBar({ progress }: { progress: PaperProgress }) {
  const labelId = `paper-${progress.paper}-progress-label`
  return (
    <div>
      <div className="flex items-baseline justify-between gap-4 text-sm">
        <span id={labelId} className="font-medium">
          Paper {progress.paper} — {progress.title}
        </span>
        <span className="tabular-nums text-content-secondary">
          {progress.topics_practiced} of {progress.total_topics} topics
        </span>
      </div>
      <div
        role="progressbar"
        aria-labelledby={labelId}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(progress.percentage)}
        className="mt-2 h-2 overflow-hidden rounded-full bg-card-border"
      >
        <div className="h-full rounded-full bg-brand" style={{ width: `${progress.percentage}%` }} />
      </div>
    </div>
  )
}

function ActivityRow({ activity }: { activity: RecentActivity }) {
  const isQuiz = activity.activity_type === 'quiz'
  return (
    <li className="flex flex-wrap items-baseline gap-x-4 gap-y-1 px-4 py-3 text-sm">
      <span className="w-10 shrink-0 font-medium tabular-nums text-brand-light">
        {activity.spec_code}
      </span>
      <span className="min-w-0 flex-1">
        {activity.title}
        <span className="text-content-secondary"> {isQuiz ? 'quiz' : 'challenge'}</span>
      </span>
      <span className="tabular-nums">
        {activity.score}/{activity.total} {isQuiz ? 'correct' : 'tests passed'}
      </span>
      <time dateTime={activity.occurred_at} className="text-content-secondary">
        {DATE_FORMAT.format(new Date(activity.occurred_at))}
      </time>
    </li>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const { data, error, isLoading, reload } = useFetch<DashboardMetrics>('/dashboard/metrics')
  const firstName = user?.full_name.split(' ')[0]

  return (
    <>
      <PageHeader
        title={firstName ? `Welcome back, ${firstName}` : 'Dashboard'}
        description="Your progress through the OCR H446 specification."
      />
      {isLoading && <Spinner label="Loading your progress" />}
      {error !== null && <ErrorAlert message={error} onRetry={reload} />}
      {data !== null && (
        <div className="space-y-10">
          <dl className="grid gap-4 sm:grid-cols-3">
            <Stat
              label="Topics practised"
              value={`${data.topics_practiced}/${data.total_topics}`}
              detail="Topics with at least one quiz attempt"
            />
            <Stat
              label="Quiz accuracy"
              value={`${Math.round(data.average_quiz_accuracy)}%`}
              detail="Correct answers across all your quizzes"
            />
            <Stat
              label="Challenges solved"
              value={`${data.challenges_solved}/${data.total_challenges}`}
              detail="Coding challenges with every test passing"
            />
          </dl>

          <section aria-labelledby="paper-progress-heading">
            <h2 id="paper-progress-heading" className="mb-4 text-lg font-semibold">
              Progress by paper
            </h2>
            <div className="space-y-5 rounded-lg border border-card-border bg-surface p-5">
              <PaperProgressBar progress={data.paper1_progress} />
              <PaperProgressBar progress={data.paper2_progress} />
            </div>
          </section>

          <section aria-labelledby="recent-activity-heading">
            <h2 id="recent-activity-heading" className="mb-4 text-lg font-semibold">
              Recent activity
            </h2>
            {data.recent_activity.length === 0 ? (
              <p className="text-sm text-content-secondary">
                Nothing yet.{' '}
                <Link to="/mcqs" className={LINK_CLASSES}>
                  Take a quiz
                </Link>{' '}
                or{' '}
                <Link to="/challenges" className={LINK_CLASSES}>
                  try a coding challenge
                </Link>{' '}
                to start tracking your progress.
              </p>
            ) : (
              <ul className="divide-y divide-card-border overflow-hidden rounded-lg border border-card-border bg-surface">
                {data.recent_activity.map((activity) => (
                  <ActivityRow
                    key={`${activity.activity_type}-${activity.occurred_at}-${activity.title}`}
                    activity={activity}
                  />
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </>
  )
}
