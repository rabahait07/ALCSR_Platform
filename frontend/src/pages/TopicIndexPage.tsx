import { PageHeader } from '../components/PageHeader'
import { TopicSelector } from '../components/TopicSelector'

interface TopicIndexPageProps {
  title: string
  description: string
  /** Route the topic choices link under, e.g. "/worksheets". */
  basePath: string
  /** Use "section" when the choice is a whole section, as for exam question packs. */
  mode?: 'subtopic' | 'section'
}

/** The "choose a topic" page for Worksheets, Notes and Exam Questions. */
export function TopicIndexPage({ title, description, basePath, mode }: TopicIndexPageProps) {
  return (
    <>
      <PageHeader title={title} description={description} />
      <TopicSelector basePath={basePath} mode={mode} />
    </>
  )
}
