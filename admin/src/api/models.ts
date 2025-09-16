import { apiClient } from './client'
import { Model, ModelCreate, ModelUpdate, ModelListResponse, ModelInfo, ModelDetails } from '@/types'

interface CompatibleModelsResponse {
  models: ModelInfo[]
  total: number
  page: number
  limit: number
}

export const modelApi = {
  // Get all models with pagination and search
  getAll: async (params?: {
    page?: number
    page_size?: number
    search?: string
    provider_id?: string
  }) => {
    const { data } = await apiClient.get<ModelListResponse>('/model/', { params })
    return data
  },

  // Get a specific model by ID
  getById: async (id: string) => {
    const { data } = await apiClient.get<Model>(`/model/${id}`)
    return data
  },

  // Create a new model
  create: async (model: ModelCreate) => {
    const { data } = await apiClient.post<Model>('/model/', model)
    return data
  },

  // Update a model
  update: async (id: string, updates: ModelUpdate) => {
    const { data } = await apiClient.patch<Model>(`/model/${id}`, updates)
    return data
  },

  // Delete a model
  delete: async (id: string) => {
    await apiClient.delete(`/model/${id}`)
  },

  // Get compatible models for an engine
  getCompatibleModels: async (params: {
    engine: 'litellm' | 'tensorzero'
    engine_version?: string
    page?: number
    limit?: number
  }) => {
    const { data } = await apiClient.get<CompatibleModelsResponse>('/model/get-compatible-models', { params })
    return data
  },

  // Get model details by URI
  getModelDetails: async (modelUri: string) => {
    const { data } = await apiClient.get<ModelDetails>(`/model/models/${modelUri}/details`)
    return data
  },

  // Update model details (description, features, pricing, etc.)
  updateModelDetails: async (id: string, details: Partial<ModelDetails>) => {
    const { data } = await apiClient.patch<ModelDetails>(`/model/${id}/details`, details)
    return data
  },
}