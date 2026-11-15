import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { ChallengesPage } from './pages/ChallengesPage'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { McqsPage } from './pages/McqsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PastPapersPage } from './pages/PastPapersPage'
import { SignupPage } from './pages/SignupPage'
import { TopicIndexPage } from './pages/TopicIndexPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Everything below needs a signed-in user and is shown under the navigation bar. */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route
                path="/worksheets"
                element={
                  <TopicIndexPage
                    title="OCR Computer Science Worksheets"
                    description="Choose a topic to see its worksheets and answers."
                    basePath="/worksheets"
                  />
                }
              />
              <Route
                path="/notes"
                element={
                  <TopicIndexPage
                    title="OCR Computer Science Notes"
                    description="Choose a topic to see its learning notes and reviewing notes."
                    basePath="/notes"
                  />
                }
              />
              <Route
                path="/exam-questions"
                element={
                  <TopicIndexPage
                    title="OCR Computer Science Exam Questions"
                    description="Choose a section to see its exam question packs and mark schemes."
                    basePath="/exam-questions"
                    mode="section"
                  />
                }
              />
              <Route path="/past-papers" element={<PastPapersPage />} />
              <Route path="/mcqs" element={<McqsPage />} />
              <Route path="/challenges" element={<ChallengesPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
