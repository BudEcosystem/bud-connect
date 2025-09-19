import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/main-layout'
import { DashboardPage } from '@/pages/dashboard'
import { LicensesPage } from '@/pages/licenses'
import { ModelsPage } from '@/pages/models'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="licenses" element={<LicensesPage />} />
            <Route path="models" element={<ModelsPage />} />
            <Route path="providers" element={<div>Providers Page (Coming Soon)</div>} />
            <Route path="engines" element={<div>Engines Page (Coming Soon)</div>} />
            <Route path="settings" element={<div>Settings Page (Coming Soon)</div>} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
