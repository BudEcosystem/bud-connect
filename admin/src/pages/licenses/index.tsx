import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { licenseApi } from '@/api'
import { License } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
import { Plus, Search, Edit, Trash2, FileText } from 'lucide-react'

const suitabilityColors = {
  MOST: 'success',
  GOOD: 'secondary',
  LOW: 'warning',
  WORST: 'destructive',
} as const

export function LicensesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [selectedSuitability, setSelectedSuitability] = useState<string>('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['licenses', page, searchTerm, selectedSuitability],
    queryFn: () => licenseApi.getAll({
      page,
      page_size: 10,
      search: searchTerm || undefined,
      suitability: selectedSuitability || undefined,
    }),
  })

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this license?')) {
      try {
        await licenseApi.delete(id)
        // Refetch data after deletion
        window.location.reload()
      } catch (error) {
        console.error('Failed to delete license:', error)
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">License Management</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add License
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Licenses</CardTitle>
          <div className="flex gap-4 mt-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="Search licenses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={selectedSuitability}
              onChange={(e) => setSelectedSuitability(e.target.value)}
              className="px-3 py-2 border rounded-md bg-background"
            >
              <option value="">All Suitabilities</option>
              <option value="MOST">Most Suitable</option>
              <option value="GOOD">Good</option>
              <option value="LOW">Low</option>
              <option value="WORST">Worst</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">Loading licenses...</div>
          ) : error ? (
            <div className="text-center py-8 text-destructive">
              Error loading licenses
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Key</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Suitability</TableHead>
                    <TableHead>FAQs</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data?.licenses.map((license: License) => (
                    <TableRow key={license.id}>
                      <TableCell className="font-mono">{license.key}</TableCell>
                      <TableCell>{license.name}</TableCell>
                      <TableCell>{license.type}</TableCell>
                      <TableCell>
                        <Badge variant={suitabilityColors[license.type_suitability]}>
                          {license.type_suitability}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {license.faqs?.length || 0} items
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="icon">
                            <FileText className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(license.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data && data.total > 10 && (
                <div className="flex justify-between items-center mt-4">
                  <div className="text-sm text-muted-foreground">
                    Showing {((page - 1) * 10) + 1} to {Math.min(page * 10, data.total)} of {data.total} licenses
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