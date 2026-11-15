import { useMemo } from 'react'

import { ErrorAlert } from '../components/ErrorAlert'
import { PageHeader } from '../components/PageHeader'
import { TopicSelector } from '../components/TopicSelector'
import { useFetch } from '../hooks/useFetch'
import type { QuizTopicsData, TopicProgressMap } from '../types'

export function McqsPage() {
  const { data, error, reload } = useFetch<QuizTopicsData>('/quizzes/topics')

  const progressMap = useMemo<TopicProgressMap | undefined>(() => {
    if (data === null) {
      return undefined
    }
    return Object.fromEntries(
      data.topics.map((topic) => [
        topic.spec_code,
        {
          attempts: topic.attempts_count,
          bestScore: topic.best_score,
          total: topic.total_questions,
        },
      ]),
    )
  }, [data])

  return (
    <>
      <PageHeader
        title="OCR Computer Science MCQs"
        description="Choose a topic to take its quiz. Your best score appears beside each topic you have attempted."
      />
      {error !== null && (
        <div className="mb-6">
          <ErrorAlert message={`Your scores could not be loaded. ${error}`} onRetry={reload} />
        </div>
      )}
      <TopicSelector basePath="/mcqs" progressMap={progressMap} />
    </>
  )
}
