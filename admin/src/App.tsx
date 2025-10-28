import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SimpleDashboard } from './components/SimpleDashboard'
import { SimpleLicenses } from './components/SimpleLicenses'
import { SimpleProviders } from './components/SimpleProviders'
import { SimpleModels } from './components/SimpleModels'
import { SimpleEngines } from './components/SimpleEngines'
import { SimpleArchitectures } from './components/SimpleArchitectures'
import Login from './components/Login'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { LogOut } from 'lucide-react'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

function AppContent() {
  const { user, logout, isAuthenticated } = useAuth();

  // Show login page without sidebar
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <div style={{ 
        width: '250px', 
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRight: '1px solid #dee2e6'
      }}>
        <h2 style={{ marginBottom: '20px' }}>BudConnect Admin</h2>
        {user && (
          <div style={{ 
            marginBottom: '20px', 
            padding: '10px', 
            backgroundColor: 'white', 
            borderRadius: '4px' 
          }}>
            <div style={{ fontWeight: 'bold' }}>{user.username}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {user.is_admin ? 'Admin' : 'User'}
            </div>
          </div>
        )}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <Link to="/" style={{ 
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            📊 Dashboard
          </Link>
          <Link to="/licenses" style={{ 
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            🔒 Licenses
          </Link>
          <Link to="/models" style={{ 
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            🤖 Models
          </Link>
          <Link to="/providers" style={{ 
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            🏢 Providers
          </Link>
          <Link to="/engines" style={{
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            ⚙️ Engines
          </Link>
          <Link to="/architectures" style={{
            padding: '10px',
            textDecoration: 'none',
            color: '#333',
            borderRadius: '4px',
            backgroundColor: 'white'
          }}>
            🏛️ Architectures
          </Link>
        </nav>
        <button
          onClick={logout}
          style={{
            marginTop: '20px',
            width: '100%',
            padding: '10px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '5px'
          }}
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
      
      {/* Main Content */}
      <div style={{ flex: 1, padding: '20px', overflow: 'auto' }}>
        <Routes>
          <Route path="/" element={<SimpleDashboard />} />
          <Route path="/licenses" element={<SimpleLicenses />} />
          <Route path="/models" element={<SimpleModels />} />
          <Route path="/providers" element={<SimpleProviders />} />
          <Route path="/engines" element={<SimpleEngines />} />
          <Route path="/architectures" element={<SimpleArchitectures />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  // Use basename for the router when deployed under /admin path
  const basename = import.meta.env.BASE_URL || '/';
  
  return (
    <QueryClientProvider client={queryClient}>
      <Router basename={basename}>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  )
}

export default App
