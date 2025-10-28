import { apiClient } from './client'
import {
  ModelArchitecture,
  ModelArchitectureCreate,
  ModelArchitectureUpdate,
  ArchitectureListResponse
} from '@/types'

export const architectureApi = {
  // Get all architectures with pagination and search
  getAll: async (params?: {
    page?: number
    page_size?: number
    search?: string
  }) => {
    const { data } = await apiClient.get<ArchitectureListResponse>('/model/architectures', { params })
    return data
  },

  // Get a specific architecture by ID
  getById: async (id: string) => {
    const { data } = await apiClient.get<ModelArchitecture>(`/model/architectures/${id}`)
    return data
  },

  // Create a new architecture
  create: async (architecture: ModelArchitectureCreate) => {
    const { data } = await apiClient.post<ModelArchitecture>('/model/architectures', architecture)
    return data
  },

  // Update an architecture
  update: async (id: string, updates: ModelArchitectureUpdate) => {
    const { data } = await apiClient.patch<ModelArchitecture>(`/model/architectures/${id}`, updates)
    return data
  },

  // Delete an architecture
  delete: async (id: string) => {
    await apiClient.delete(`/model/architectures/${id}`)
  },
}