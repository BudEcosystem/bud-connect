import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { modelApi } from '@/api'
import { ModelInfo } from '@/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Database, Info, DollarSign } from 'lucide-react'

export function ModelsPage() {
  const [engine, setEngine] = useState<'litellm' | 'tensorzero'>('litellm')
  const [page, setPage] = useState(1)

  const { data, isLoading, error } = useQuery({
    queryKey: ['models', engine, page],
    queryFn: () => modelApi.getCompatibleModels({
      engine,
      page,
      limit: 10,
    }),
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Model Management</h1>
        <div className="flex gap-2">
          <Button
            variant={engine === 'litellm' ? 'default' : 'outline'}
            onClick={() => setEngine('litellm')}
          >
            LiteLLM
          </Button>
          <Button
            variant={engine === 'tensorzero' ? 'default' : 'outline'}
            onClick={() => setEngine('tensorzero')}
          >
            TensorZero
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <Database className="inline-block mr-2 h-5 w-5" />
            Compatible Models for {engine}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">Loading models...</div>
          ) : error ? (
            <div className="text-center py-8 text-destructive">
              Error loading models
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Model URI</TableHead>
                    <TableHead>Modality</TableHead>
                    <TableHead>Provider</TableHead>
                    <TableHead>Features</TableHead>
                    <TableHead>Pricing</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data?.models?.map((model: ModelInfo) => (
                    <TableRow key={model.id}>
                      <TableCell className="font-mono text-sm">
                        {model.uri}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {model.modality?.map((m) => (
                            <Badge key={m} variant="outline" className="text-xs">
                              {m}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        {model.provider?.name || 'Unknown'}
                      </TableCell>
                      <TableCell>
                        {model.features && Object.keys(model.features).length > 0 ? (
                          <Badge variant="secondary">
                            {Object.keys(model.features).length} features
                          </Badge>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {model.input_cost || model.output_cost ? (
                          <DollarSign className="h-4 w-4 text-green-600" />
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="icon">
                          <Info className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data && data.total > 10 && (
                <div className="flex justify-between items-center mt-4">
                  <div className="text-sm text-muted-foreground">
                    Showing {((page - 1) * 10) + 1} to {Math.min(page * 10, data.total)} of {data.total} models
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => p + 1)}
                      disabled={page * 10 >= (data?.total || 0)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}