import { apiClient } from './client'
import { License, LicenseCreate, LicenseUpdate } from '@/types'

interface LicenseListResponse {
  licenses: License[]
  total: number
  page: number
  page_size: number
}

export const licenseApi = {
  // Get all licenses with pagination and filters
  getAll: async (params?: {
    page?: number
    page_size?: number
    license_type?: string
    suitability?: string
    search?: string
  }) => {
    const { data } = await apiClient.get<LicenseListResponse>('/licenses/', { params })
    return data
  },

  // Get a specific license by ID
  getById: async (id: string) => {
    const { data } = await apiClient.get<License>(`/licenses/${id}`)
    return data
  },

  // Get a license by key
  getByKey: async (key: string) => {
    const { data } = await apiClient.get<License>(`/licenses/key/${key}`)
    return data
  },

  // Create a new license
  create: async (license: LicenseCreate) => {
    const { data } = await apiClient.post<License>('/licenses/', license)
    return data
  },

  // Update a license
  update: async (id: string, updates: LicenseUpdate) => {
    const { data } = await apiClient.patch<License>(`/licenses/${id}`, updates)
    return data
  },

  // Delete a license
  delete: async (id: string) => {
    await apiClient.delete(`/licenses/${id}`)
  },

  // Extract license information
  extract: async (request: { source_type: string; source: string; key?: string }) => {
    const { data } = await apiClient.post<License>('/licenses/extract', request)
    return data
  },

  // Extract and create license
  extractAndCreate: async (request: { source_type: string; source: string; key?: string }) => {
    const { data } = await apiClient.post<License>('/licenses/extract-and-create', request)
    return data
  },
}