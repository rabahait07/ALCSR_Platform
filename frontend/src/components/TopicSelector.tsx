import { useState } from 'react'
import clsx from 'clsx'
import { Check, ChevronDown } from 'lucide-react'
import { Link } from 'react-router-dom'

import { ErrorAlert } from './ErrorAlert'
import { Spinner } from './Spinner'
import { useFetch } from '../hooks/useFetch'
import type {
  MajorSection,
  PaperHierarchy,
  SyllabusTree,
  TopicProgress,
  TopicProgressMap,
} from '../types'

interface TopicSelectorProps {
  /** Route the choices link under, e.g. "/worksheets" links to "/worksheets/1.1.1". */
  basePath: string
  /**
   * "subtopic" (default) lists each section's sub-topics, linking by specification code.
   * "section" makes the sections themselves the choices, linking by section slug.
   */
  mode?: 'subtopic' | 'section'
  /** Progress badges for sub-topics, keyed by specification code. */
  progressMap?: TopicProgressMap
}

/** "1.3 Exchanging data" with code "1.3" becomes "Exchanging data". */
function sectionName(section: MajorSection): string {
  return section.section_title.startsWith(section.section_code)
    ? section.section_title.slice(section.section_code.length).trim()
    : section.section_title
}

function ProgressBadge({ progress }: { progress: TopicProgress }) {
  if (progress.attempts === 0 || progress.bestScore === null || progress.total === null) {
    return null
  }
  const isFullMarks = progress.bestScore === progress.total
  return (
    <span
      aria-label={`Best score ${progress.bestScore} out of ${progress.total}`}
      className={clsx(
        'flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium tabular-nums',
        isFullMarks ? 'bg-emerald-500/15 text-emerald-300' : 'bg-brand/15 text-brand-light',
      )}
    >
      {isFullMarks && <Check aria-hidden="true" className="h-3 w-3" />}
      {progress.bestScore}/{progress.total}
    </span>
  )
}

const ROW_CLASSES =
  'flex items-baseline gap-4 px-4 py-3 text-sm transition-colors hover:bg-obsidian focus-visible:bg-obsidian'
const CODE_CLASSES = 'w-10 shrink-0 font-medium tabular-nums text-brand-light'

interface PaperColumnProps extends Required<Pick<TopicSelectorProps, 'basePath' | 'mode'>> {
  paper: PaperHierarchy
  progressMap: TopicProgressMap | undefined
  collapsed: ReadonlySet<string>
  onToggle: (sectionCode: string) => void
}

function PaperColumn({ paper, basePath, mode, progressMap, collapsed, onToggle }: PaperColumnProps) {
  const headingId = `paper-${paper.paper}-heading`

  return (
    <section aria-labelledby={headingId}>
      <h2 id={headingId} className="mb-4 text-lg font-semibold">
        Paper {paper.paper} — {paper.title}
      </h2>

      {paper.sections.length === 0 && (
        <p className="text-sm text-content-secondary">No topics are available for this paper yet.</p>
      )}

      {mode === 'section' && paper.sections.length > 0 && (
        <ul className="divide-y divide-card-border overflow-hidden rounded-lg border border-card-border bg-surface">
          {paper.sections.map((section) => (
            <li key={section.section_code}>
              <Link to={`${basePath}/${section.section_slug}`} className={ROW_CLASSES}>
                <span className={CODE_CLASSES}>{section.section_code}</span>
                <span className="flex-1">{sectionName(section)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      {mode === 'subtopic' && (
        <div className="space-y-4">
          {paper.sections.map((section) => {
            const isOpen = !collapsed.has(section.section_code)
            const listId = `section-${section.section_slug}-topics`
            return (
              <div
                key={section.section_code}
                className="overflow-hidden rounded-lg border border-card-border bg-surface"
              >
                <h3>
                  <button
                    type="button"
                    onClick={() => onToggle(section.section_code)}
                    aria-expanded={isOpen}
                    aria-controls={listId}
                    className="flex w-full items-baseline gap-4 px-4 py-3 text-left text-sm font-semibold transition-colors hover:bg-obsidian"
                  >
                    <span className="w-10 shrink-0 tabular-nums">{section.section_code}</span>
                    <span className="flex-1">{sectionName(section)}</span>
                    <ChevronDown
                      aria-hidden="true"
                      className={clsx(
                        'h-4 w-4 shrink-0 self-center text-content-secondary transition-transform motion-reduce:transition-none',
                        isOpen && 'rotate-180',
                      )}
                    />
                  </button>
                </h3>
                <ul
                  id={listId}
                  hidden={!isOpen}
                  className="divide-y divide-card-border border-t border-card-border"
                >
                  {section.subtopics.map((subtopic) => {
                    const progress = progressMap?.[subtopic.spec_code]
                    return (
                      <li key={subtopic.spec_code}>
                        <Link to={`${basePath}/${subtopic.spec_code}`} className={ROW_CLASSES}>
                          <span className={CODE_CLASSES}>{subtopic.spec_code}</span>
                          <span className="flex-1 text-content-secondary">{subtopic.title}</span>
                          {progress && <ProgressBadge progress={progress} />}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}

/**
 * The OCR H446 syllabus as two columns, Paper 1 and Paper 2, for choosing what to study.
 * Loads the syllabus itself, so a page only needs to say where the choices should link.
 */
export function TopicSelector({ basePath, mode = 'subtopic', progressMap }: TopicSelectorProps) {
  const { data, error, isLoading, reload } = useFetch<SyllabusTree>('/syllabus/tree')
  const [collapsed, setCollapsed] = useState<ReadonlySet<string>>(new Set())

  const toggleSection = (sectionCode: string) => {
    setCollapsed((current) => {
      const next = new Set(current)
      if (!next.delete(sectionCode)) {
        next.add(sectionCode)
      }
      return next
    })
  }

  if (isLoading) {
    return <Spinner label="Loading the syllabus" />
  }
  if (error !== null || data === null) {
    return <ErrorAlert message={error ?? 'The syllabus could not be loaded.'} onRetry={reload} />
  }

  return (
    <div className="grid items-start gap-x-8 gap-y-10 lg:grid-cols-2">
      {data.papers.map((paper) => (
        <PaperColumn
          key={paper.paper}
          paper={paper}
          basePath={basePath}
          mode={mode}
          progressMap={progressMap}
          collapsed={collapsed}
          onToggle={toggleSection}
        />
      ))}
    </div>
  )
}
