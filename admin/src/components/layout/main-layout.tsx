import { Link, Outlet, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { 
  Database, 
  Shield, 
  Cpu, 
  Box, 
  LayoutDashboard,
  Settings 
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Licenses', href: '/licenses', icon: Shield },
  { name: 'Models', href: '/models', icon: Database },
  { name: 'Providers', href: '/providers', icon: Box },
  { name: 'Engines', href: '/engines', icon: Cpu },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function MainLayout() {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex w-64 flex-col">
          <div className="flex min-h-0 flex-1 flex-col border-r bg-card">
            <div className="flex flex-1 flex-col overflow-y-auto pb-4">
              <div className="flex items-center h-16 flex-shrink-0 px-4 border-b">
                <h1 className="text-xl font-bold">BudConnect Admin</h1>
              </div>
              <nav className="mt-5 flex-1 space-y-1 px-2">
                {navigation.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.href || 
                    (item.href !== '/' && location.pathname.startsWith(item.href))
                  
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={cn(
                        isActive
                          ? 'bg-secondary text-foreground'
                          : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground',
                        'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                      )}
                    >
                      <Icon
                        className={cn(
                          isActive ? 'text-foreground' : 'text-muted-foreground',
                          'mr-3 h-5 w-5 flex-shrink-0'
                        )}
                      />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        <main className="flex-1 overflow-y-auto">
          <div className="py-6">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}