/**
 * Shapes of the JSON the backend returns and accepts. Field names match the Pydantic schemas
 * in backend/app/schemas exactly, so they stay in snake_case.
 */

// --- Auth ------------------------------------------------------------------------------------

export interface User {
  id: number
  full_name: string
  email: string
  /** ISO 8601 timestamp in UTC. */
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// --- Syllabus --------------------------------------------------------------------------------

export type PaperNumber = 1 | 2

export interface Subtopic {
  id: number
  /** Specification code, e.g. "1.1.1". */
  spec_code: string
  title: string
  slug: string
}

export interface MajorSection {
  /** Section code, e.g. "1.3". */
  section_code: string
  /** Section title including its code, e.g. "1.3 Exchanging data". */
  section_title: string
  /** URL form of the section code, e.g. "1-3". */
  section_slug: string
  subtopics: Subtopic[]
}

export interface PaperHierarchy {
  paper: PaperNumber
  title: string
  sections: MajorSection[]
}

export interface SyllabusTree {
  papers: PaperHierarchy[]
}

// --- Static resources ------------------------------------------------------------------------

export type ResourceType =
  | 'worksheet'
  | 'worksheet_answer'
  | 'learning_note'
  | 'reviewing_note'
  | 'exam_pack'
  | 'mark_scheme'
  | 'past_paper_qp'
  | 'past_paper_ms'
  | 'past_paper_walkthrough'

export interface ResourceItem {
  id: number
  resource_type: ResourceType
  title: string
  /** Static PDF path or external URL. Always opened with a plain new-tab link. */
  file_url: string
  display_order: number
}

/**
 * Resources for one sub-topic. The worksheets endpoint returns `worksheets` and `answers`;
 * the notes endpoint returns `learning_notes` and `reviewing_notes`.
 */
export interface TopicResources {
  topic: Subtopic
  worksheets?: ResourceItem[]
  answers?: ResourceItem[]
  learning_notes?: ResourceItem[]
  reviewing_notes?: ResourceItem[]
}

export interface ExamSectionResources {
  paper: PaperNumber
  section_code: string
  section_title: string
  section_slug: string
  exam_packs: ResourceItem[]
  mark_schemes: ResourceItem[]
}

export interface PastPaperRow {
  paper: PaperNumber
  /** Exam series, e.g. "June 2024" or "Specimen". */
  exam_series: string
  question_paper_url: string | null
  mark_scheme_url: string | null
  walkthrough_url: string | null
}

export interface PastPapersData {
  paper_1: PastPaperRow[]
  paper_2: PastPaperRow[]
}

// --- Quizzes ---------------------------------------------------------------------------------

/** A question before submission. The correct answer is never part of this shape. */
export interface MCQQuestionPublic {
  id: number
  topic_id: number
  question_text: string
  code_snippet: string | null
  options: string[]
}

export interface Quiz {
  topic: Subtopic
  questions: MCQQuestionPublic[]
}

/** Request body for submitting a quiz: question id mapped to the chosen option index. */
export interface QuizSubmission {
  answers: Record<number, number>
}

export interface QuestionResult {
  question_id: number
  selected_index: number | null
  correct_index: number
  is_correct: boolean
  explanation: string
}

export interface QuizResult {
  attempt_id: number
  topic_id: number
  score: number
  total_questions: number
  percentage: number
  results: QuestionResult[]
}

export interface QuizTopicSummary {
  id: number
  paper: PaperNumber
  section_code: string
  spec_code: string
  title: string
  slug: string
  /** Questions available for the sub-topic; 0 means there is no quiz yet. */
  question_count: number
  attempts_count: number
  /** Score of the best attempt, or null if never attempted. */
  best_score: number | null
  /** Length of the best attempt, or null if never attempted. */
  total_questions: number | null
}

export interface QuizTopicsData {
  topics: QuizTopicSummary[]
}

// --- Coding challenges -----------------------------------------------------------------------

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

export type Difficulty = 'Easy' | 'Medium' | 'Hard'

export interface TestCase {
  input_args: JsonValue[]
  expected: JsonValue
  description: string
}

export interface CodingChallengeSummary {
  id: number
  topic_id: number
  slug: string
  title: string
  difficulty: Difficulty
  solved: boolean
  attempts_count: number
}

export interface CodingChallengeDetail {
  id: number
  topic_id: number
  slug: string
  title: string
  difficulty: Difficulty
  /** Markdown. */
  description: string
  function_name: string
  starter_code: string
  test_cases: TestCase[]
  solved: boolean
  /** Code from the user's most recent submission, or null if never attempted. */
  latest_code: string | null
}

/** Request body for submitting a challenge, as reported by the in-browser runner. */
export interface ChallengeSubmissionPayload {
  code: string
  passed: boolean
  passed_tests: number
  /** Must equal the number of test cases the challenge has. */
  total_tests: number
}

export interface ChallengeSubmissionResult {
  id: number
  challenge_id: number
  code: string
  passed: boolean
  passed_tests: number
  total_tests: number
  /** ISO 8601 timestamp in UTC. */
  submitted_at: string
}

// --- Dashboard -------------------------------------------------------------------------------

export interface RecentActivity {
  activity_type: 'quiz' | 'challenge'
  title: string
  spec_code: string
  score: number
  total: number
  /** ISO 8601 timestamp in UTC. */
  occurred_at: string
}

export interface PaperProgress {
  paper: PaperNumber
  title: string
  topics_practiced: number
  total_topics: number
  percentage: number
}

export interface DashboardMetrics {
  topics_practiced: number
  total_topics: number
  average_quiz_accuracy: number
  challenges_solved: number
  total_challenges: number
  paper1_progress: PaperProgress
  paper2_progress: PaperProgress
  recent_activity: RecentActivity[]
}

// --- UI --------------------------------------------------------------------------------------

/** Progress shown as a badge on a sub-topic in the topic selector, keyed by spec code. */
export interface TopicProgress {
  attempts: number
  bestScore: number | null
  total: number | null
}

export type TopicProgressMap = Record<string, TopicProgress>
