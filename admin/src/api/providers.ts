import { apiClient } from './client'
import { Provider, ProviderCreate, ProviderUpdate } from '@/types'

interface ProviderListResponse {
  providers: Provider[]
  total: number
  page: number
  page_size: number
}

export const providerApi = {
  // Get all providers with pagination and search
  getAll: async (params?: {
    page?: number
    page_size?: number
    search?: string
  }) => {
    const { data } = await apiClient.get<ProviderListResponse>('/providers/', { params })
    return data
  },

  // Get a specific provider by ID
  getById: async (id: string) => {
    const { data } = await apiClient.get<Provider>(`/providers/${id}`)
    return data
  },

  // Create a new provider
  create: async (provider: ProviderCreate) => {
    const { data } = await apiClient.post<Provider>('/providers/', provider)
    return data
  },

  // Update a provider
  update: async (id: string, updates: ProviderUpdate) => {
    const { data } = await apiClient.patch<Provider>(`/providers/${id}`, updates)
    return data
  },

  // Delete a provider
  delete: async (id: string) => {
    await apiClient.delete(`/providers/${id}`)
  },
}