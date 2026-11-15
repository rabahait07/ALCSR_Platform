import { ErrorAlert } from '../components/ErrorAlert'
import { PageHeader } from '../components/PageHeader'
import { Spinner } from '../components/Spinner'
import { useFetch } from '../hooks/useFetch'
import type { PastPaperRow, PastPapersData } from '../types'

const DOCUMENTS = [
  { key: 'question_paper_url', heading: 'Question paper', suffix: 'QP' },
  { key: 'mark_scheme_url', heading: 'Mark scheme', suffix: 'MS' },
  { key: 'walkthrough_url', heading: 'Paper walkthrough', suffix: 'PW' },
] as const

const LINK_CLASSES = 'rounded text-brand-light underline-offset-2 hover:underline'

interface PaperTableProps {
  paper: 1 | 2
  rows: PastPaperRow[]
}

function PaperTable({ paper, rows }: PaperTableProps) {
  const headingId = `past-papers-paper-${paper}`

  return (
    <section aria-labelledby={headingId}>
      <h2 id={headingId} className="mb-4 text-lg font-semibold">
        Paper {paper}
      </h2>
      {rows.length === 0 ? (
        <p className="text-sm text-content-secondary">No past papers are available for this paper yet.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-card-border bg-surface">
          <table className="w-full min-w-[36rem] text-left text-sm">
            <thead className="border-b border-card-border text-content-secondary">
              <tr>
                <th scope="col" className="px-4 py-3 font-medium">
                  Series
                </th>
                {DOCUMENTS.map(({ key, heading }) => (
                  <th key={key} scope="col" className="px-4 py-3 font-medium">
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-card-border">
              {rows.map((row) => (
                <tr key={row.exam_series}>
                  <th scope="row" className="whitespace-nowrap px-4 py-3 font-medium">
                    {row.exam_series}
                  </th>
                  {DOCUMENTS.map(({ key, suffix }) => {
                    const url = row[key]
                    return (
                      <td key={key} className="whitespace-nowrap px-4 py-3">
                        {url === null ? (
                          <span className="text-content-secondary">Not available</span>
                        ) : (
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={LINK_CLASSES}
                          >
                            {row.exam_series} Paper {paper} {suffix}
                          </a>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export function PastPapersPage() {
  const { data, error, isLoading, reload } = useFetch<PastPapersData>('/resources/past-papers')

  return (
    <>
      <PageHeader
        title="OCR Computer Science Past Papers"
        description="Question papers, mark schemes and walkthroughs for every exam series. Each link opens in a new tab."
      />
      {isLoading && <Spinner label="Loading past papers" />}
      {error !== null && <ErrorAlert message={error} onRetry={reload} />}
      {data !== null && (
        <div className="space-y-10">
          <PaperTable paper={1} rows={data.paper_1} />
          <PaperTable paper={2} rows={data.paper_2} />
        </div>
      )}
    </>
  )
}
