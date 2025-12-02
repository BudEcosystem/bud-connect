import { apiClient } from './client'
import { 
  Engine, 
  EngineCreate, 
  EngineUpdate,
  EngineVersion, 
  EngineVersionCreate,
  EngineVersionUpdate,
  EngineCompatibility,
  EngineCompatibilityCreate,
  EngineCompatibilityUpdate,
  DeviceArchitecture,
  EngineToolParserRule,
  EngineToolParserRuleCreate,
  EngineToolParserRuleUpdate,
  CompatibleEngine,
} from '@/types'

interface CompatibleEnginesResponse {
  message: string
  code: number
  object: string
  compatible_engines: CompatibleEngine[]
}

interface LatestEngineVersionResponse {
  version: string
  compatibilities: EngineCompatibility[]
  message: string
  code: number
  object: string
}

interface EngineListResponse {
  engines: Engine[]
  total: number
  page: number
  page_size: number
  message: string
  code: number
  object: string
}

interface EngineResponse {
  engine: Engine
  message: string
  code: number
  object: string
}

interface EngineVersionListResponse {
  versions: EngineVersion[]
  total: number
  page: number
  page_size: number
  message: string
  code: number
  object: string
}

interface EngineVersionResponse {
  version: EngineVersion
  message: string
  code: number
  object: string
}

interface EngineCompatibilityResponse {
  compatibility: EngineCompatibility
  message: string
  code: number
  object: string
}

interface ParserRuleListResponse {
  rules: EngineToolParserRule[]
  message: string
  code: number
  object: string
}

interface ParserRuleResponse {
  rule: EngineToolParserRule
  message: string
  code: number
  object: string
}

export const engineApi = {
  // Engine CRUD
  create: async (data: EngineCreate) => {
    const response = await apiClient.post<EngineResponse>('/engine/', data)
    return response.data.engine
  },

  getAll: async (params?: { page?: number; page_size?: number; search?: string }) => {
    const { data } = await apiClient.get<EngineListResponse>('/engine/', { params })
    return data
  },

  getOne: async (id: string) => {
    const { data } = await apiClient.get<EngineResponse>(`/engine/${id}`)
    return data.engine
  },

  update: async (id: string, data: EngineUpdate) => {
    const response = await apiClient.put<EngineResponse>(`/engine/${id}`, data)
    return response.data.engine
  },

  delete: async (id: string) => {
    await apiClient.delete(`/engine/${id}`)
  },

  // Engine Version CRUD
  createVersion: async (data: EngineVersionCreate) => {
    const response = await apiClient.post<EngineVersionResponse>('/engine/version/', data)
    return response.data.version
  },

  getVersions: async (params?: { engine_id?: string; page?: number; page_size?: number }) => {
    const { data } = await apiClient.get<EngineVersionListResponse>('/engine/version/', { params })
    return data
  },

  getVersion: async (id: string) => {
    const { data } = await apiClient.get<EngineVersionResponse>(`/engine/version/${id}`)
    return data.version
  },

  updateVersion: async (id: string, data: EngineVersionUpdate) => {
    const response = await apiClient.put<EngineVersionResponse>(`/engine/version/${id}`, data)
    return response.data.version
  },

  deleteVersion: async (id: string) => {
    await apiClient.delete(`/engine/version/${id}`)
  },

  // Engine Compatibility CRUD
  createCompatibility: async (data: EngineCompatibilityCreate) => {
    const response = await apiClient.post<EngineCompatibilityResponse>('/engine/compatibility/', data)
    return response.data.compatibility
  },

  updateCompatibility: async (id: string, data: EngineCompatibilityUpdate) => {
    const response = await apiClient.put<EngineCompatibilityResponse>(`/engine/compatibility/${id}`, data)
    return response.data.compatibility
  },

  deleteCompatibility: async (id: string) => {
    await apiClient.delete(`/engine/compatibility/${id}`)
  },

  // Engine parser rules
  getParserRules: async (engineId: string) => {
    const { data } = await apiClient.get<ParserRuleListResponse>(`/engine/parser-rules/${engineId}`)
    return data
  },

  createParserRule: async (data: EngineToolParserRuleCreate) => {
    const response = await apiClient.post<ParserRuleResponse>('/engine/parser-rules', data)
    return response.data.rule
  },

  updateParserRule: async (ruleId: string, data: EngineToolParserRuleUpdate) => {
    const response = await apiClient.put<ParserRuleResponse>(`/engine/parser-rules/${ruleId}`, data)
    return response.data.rule
  },

  deleteParserRule: async (ruleId: string) => {
    await apiClient.delete(`/engine/parser-rules/${ruleId}`)
  },

  // Legacy endpoints
  getCompatibleEngines: async (params: {
    model_architecture: string
    device_architecture?: DeviceArchitecture
    engine_version?: string
    engine?: string
  }) => {
    const { data } = await apiClient.get<CompatibleEnginesResponse>('/engine/get-compatible-engines', { params })
    return data
  },

  getLatestEngineVersion: async (params: {
    device_architecture: DeviceArchitecture
    engine: string
  }) => {
    const { data } = await apiClient.get<LatestEngineVersionResponse>('/engine/get-latest-engine-version', { params })
    return data
  },
}
