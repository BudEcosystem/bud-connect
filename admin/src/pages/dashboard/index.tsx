import { useQuery } from '@tanstack/react-query'
import { licenseApi, modelApi } from '@/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Database, Shield, Box, Cpu } from 'lucide-react'

export function DashboardPage() {
  const { data: licenses } = useQuery({
    queryKey: ['licenses-summary'],
    queryFn: () => licenseApi.getAll({ page: 1, page_size: 5 }),
  })

  const { data: litellmModels } = useQuery({
    queryKey: ['models-litellm-summary'],
    queryFn: () => modelApi.getCompatibleModels({ 
      engine: 'litellm', 
      page: 1, 
      limit: 5 
    }),
  })

  const { data: tensorzeroModels } = useQuery({
    queryKey: ['models-tensorzero-summary'],
    queryFn: () => modelApi.getCompatibleModels({ 
      engine: 'tensorzero', 
      page: 1, 
      limit: 5 
    }),
  })

  const stats = [
    {
      title: 'Total Licenses',
      value: licenses?.total || 0,
      icon: Shield,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'LiteLLM Models',
      value: litellmModels?.total || 0,
      icon: Database,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'TensorZero Models',
      value: tensorzeroModels?.total || 0,
      icon: Database,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Active Engines',
      value: 2,
      icon: Cpu,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome to BudConnect Admin Panel
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.bgColor} p-2 rounded-lg`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Licenses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {licenses?.licenses.slice(0, 5).map((license) => (
                <div key={license.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{license.name}</p>
                    <p className="text-sm text-muted-foreground">{license.key}</p>
                  </div>
                  <Badge variant={
                    license.type_suitability === 'MOST' ? 'success' :
                    license.type_suitability === 'GOOD' ? 'secondary' :
                    license.type_suitability === 'LOW' ? 'warning' :
                    'destructive'
                  }>
                    {license.type_suitability}
                  </Badge>
                </div>
              ))}
              {!licenses?.licenses.length && (
                <p className="text-sm text-muted-foreground">No licenses available</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>API Server</span>
                </div>
                <Badge variant="success">Healthy</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>Database</span>
                </div>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-green-500"></div>
                  <span>Redis Cache</span>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
                  <span>Dapr Runtime</span>
                </div>
                <Badge variant="warning">Initializing</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}