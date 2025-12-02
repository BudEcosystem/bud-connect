// License Types
export interface License {
  id: string
  key: string
  name: string
  type: string
  type_description: string
  type_suitability: 'MOST' | 'GOOD' | 'LOW' | 'WORST'
  faqs: FAQ[]
  created_at?: string
  updated_at?: string
}

export interface FAQ {
  question: string
  answer: string
  reason?: string[]
  impact?: string
}

export interface LicenseCreate {
  key: string
  name: string
  type: string
  type_description: string
  type_suitability: 'MOST' | 'GOOD' | 'LOW' | 'WORST'
  faqs: FAQ[]
}

export interface LicenseUpdate {
  key?: string
  name?: string
  type?: string
  type_description?: string
  type_suitability?: 'MOST' | 'GOOD' | 'LOW' | 'WORST'
  faqs?: FAQ[]
}

// Provider Types
export interface CredentialField {
  field: string
  label: string
  type: 'password' | 'text' | 'select' | 'number'
  description: string
  required: boolean
  order: number
  options?: string[]
  default?: string
}

export interface Provider {
  id: string
  name: string
  provider_type: string
  icon: string
  description: string
  credentials: CredentialField[]
  model_count?: number
  created_at?: string
  modified_at?: string
}

export interface ProviderCreate {
  name: string
  provider_type: string
  icon: string
  description: string
  credentials: CredentialField[]
}

export interface ProviderUpdate {
  name?: string
  icon?: string
  description?: string
  credentials?: CredentialField[]
}

// Model Architecture Types
export interface ModelArchitecture {
  id: string
  class_name: string
  architecture_family: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  supports_lora: boolean
  supports_pipeline_parallelism: boolean
  model_count?: number
  created_at: string
  modified_at: string
}

export interface ModelArchitectureCreate {
  class_name: string
  architecture_family: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  supports_lora?: boolean
  supports_pipeline_parallelism?: boolean
}

export interface ModelArchitectureUpdate {
  architecture_family?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  supports_lora?: boolean
  supports_pipeline_parallelism?: boolean
}

export interface ArchitectureListResponse {
  architectures: ModelArchitecture[]
  total: number
  page: number
  page_size: number
}

// Model Types
export type ModalityEnum = 'text_input' | 'text_output' | 'image_input' | 'image_output' | 'audio_input' | 'audio_output'
export type ModelEndpointEnum = '/v1/chat/completions' | '/v1/completions' | '/v1/images/generations' | '/v1/images/edits' | '/v1/images/variations' | '/v1/audio/transcriptions' | '/v1/audio/translations' | '/v1/audio/speech' | '/v1/embeddings' | '/v1/batch' | '/v1/responses' | '/v1/documents' | '/v1/rerank' | '/v1/moderations'

export interface InputCost {
  input_cost_per_token?: number
  input_cost_per_character?: number
  input_cost_per_image?: number
  input_cost_per_audio_per_second?: number
  input_cost_per_video_per_second?: number
  [key: string]: number | undefined
}

export interface OutputCost {
  output_cost_per_token?: number
  output_cost_per_character?: number
  output_cost_per_image?: number
  output_cost_per_second?: number
  [key: string]: number | undefined
}

export interface CacheCost {
  cache_read_input_token_cost?: number
  cache_creation_input_token_cost?: number
  [key: string]: number | undefined
}

export interface Tokens {
  input?: number
  output?: number
  total?: number
  [key: string]: number | undefined
}

export interface RateLimits {
  rpm?: number
  rpd?: number
  tpm?: number
  tpd?: number
  [key: string]: number | undefined
}

export interface MediaLimits {
  max_images?: number
  max_videos?: number
  max_audio_length?: number
  max_video_length?: number
  [key: string]: number | undefined
}

export interface Features {
  supports_function_calling?: boolean
  supports_streaming?: boolean
  supports_web_search?: boolean
  supports_response_schema?: boolean
  supports_reasoning?: boolean
  [key: string]: boolean | undefined
}

export interface Model {
  id: string
  uri: string
  modality: ModalityEnum[]
  provider_id: string
  provider_name?: string
  provider_type?: string
  model_architecture_class_id?: string
  architecture_class?: ModelArchitecture
  input_cost?: InputCost
  output_cost?: OutputCost
  cache_cost?: CacheCost
  search_context_cost_per_query?: Record<string, any>
  tokens?: Tokens
  rate_limits?: RateLimits
  media_limits?: MediaLimits
  features?: Features
  endpoints: ModelEndpointEnum[]
  deprecation_date?: string
  license?: License
  chat_template?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  created_at?: string
  modified_at?: string
}

export interface ModelCreate {
  uri: string
  modality: ModalityEnum[]
  provider_id: string
  model_architecture_class_id?: string
  input_cost?: InputCost
  output_cost?: OutputCost
  cache_cost?: CacheCost
  search_context_cost_per_query?: Record<string, any>
  tokens?: Tokens
  rate_limits?: RateLimits
  media_limits?: MediaLimits
  features?: Features
  endpoints: ModelEndpointEnum[]
  deprecation_date?: string
  license_id?: string
  chat_template?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
}

export interface ModelUpdate {
  uri?: string
  modality?: ModalityEnum[]
  provider_id?: string
  model_architecture_class_id?: string
  input_cost?: InputCost
  output_cost?: OutputCost
  cache_cost?: CacheCost
  search_context_cost_per_query?: Record<string, any>
  tokens?: Tokens
  rate_limits?: RateLimits
  media_limits?: MediaLimits
  features?: Features
  endpoints?: ModelEndpointEnum[]
  deprecation_date?: string
  license_id?: string
  chat_template?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
}

export interface ModelListResponse {
  models: Model[]
  total: number
  page: number
  page_size: number
}

// Model Types
export type Modality = 'LLM' | 'IMAGE' | 'AUDIO' | 'VIDEO' | 'EMBEDDING'
export type ModelEndpoint = 'CHAT' | 'COMPLETION' | 'EMBEDDING' | 'IMAGE_GENERATION' | 'IMAGE_EDIT' | 'IMAGE_VARIATION' | 'AUDIO_TRANSCRIPTION' | 'AUDIO_TRANSLATION' | 'AUDIO_SPEECH' | 'BATCH' | 'RESPONSE' | 'DOCUMENT' | 'RERANK' | 'MODERATION'

export interface ModelInfo {
  id: string
  uri: string
  modality?: Modality[]
  input_cost?: Record<string, any>
  output_cost?: Record<string, any>
  cache_cost?: Record<string, any>
  search_context_cost_per_query?: Record<string, any>
  tokens?: Record<string, any>
  rate_limits?: Record<string, any>
  media_limits?: Record<string, any>
  features?: Record<string, any>
  provider_id: string
  provider?: Provider
  license_id?: string
  license?: License
  model_architecture_class_id?: string
  architecture_class?: ModelArchitecture
  deprecation_date?: string
  endpoints?: ModelEndpoint[]
  details?: ModelDetails
  chat_template?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  created_at?: string
  updated_at?: string
}

export interface ModelDetails {
  id: string
  model_info_id: string
  description?: string
  advantages?: string[]
  disadvantages?: string[]
  use_cases?: string[]
  evaluations?: Array<{
    benchmark: string
    score: number
    date?: string
  }>
  languages?: string[]
  tags?: string[]
  tasks?: string[]
  papers?: Array<{
    title: string
    url: string
    year?: number
  }>
  github_url?: string
  website_url?: string
  logo_url?: string
  architecture?: Record<string, any>
  model_tree?: Record<string, any>
  extraction_metadata?: Record<string, any>
  tool_calling_parser_type?: string | null
}

// Engine Types
export type DeviceArchitecture = 'CUDA' | 'CPU' | 'ROCM' | 'HPU'

export interface Engine {
  id: string
  name: string
  versions?: EngineVersion[]
  created_at?: string
  updated_at?: string
}

export interface EngineCreate {
  name: string
}

export interface EngineUpdate {
  name?: string
}

export interface EngineVersion {
  id: string
  engine_id: string
  version: string
  container_image: string
  device_architecture: DeviceArchitecture
  engine?: Engine
  compatibilities?: EngineCompatibility[]
  supported_providers?: Provider[]
  created_at?: string
  updated_at?: string
}

export interface EngineVersionCreate {
  engine_id: string
  version: string
  container_image: string
  device_architecture: DeviceArchitecture
}

export interface EngineVersionUpdate {
  version?: string
  container_image?: string
  device_architecture?: DeviceArchitecture
}

export interface EngineCompatibility {
  id: string
  engine_version_id: string
  architectures: Record<string, any>
  features: Record<string, any>
  engine_version?: EngineVersion
  created_at?: string
  updated_at?: string
}

export type ParserMatchType = 'exact' | 'prefix' | 'regex'

export type ParserRuleType = 'tool' | 'reasoning'

export interface EngineParserRule {
  id: string
  engine_id: string
  rule_type: ParserRuleType
  parser_type: string | null
  match_type: ParserMatchType
  pattern: string
  priority: number
  enabled: boolean
  notes?: string | null
  chat_template?: string | null
  created_at?: string
  modified_at?: string
}

export interface EngineParserRuleCreate {
  engine_id: string
  rule_type?: ParserRuleType
  parser_type?: string | null
  match_type: ParserMatchType
  pattern: string
  priority?: number
  enabled?: boolean
  notes?: string | null
  chat_template?: string | null
}

export interface EngineParserRuleUpdate {
  rule_type?: ParserRuleType
  parser_type?: string | null
  match_type?: ParserMatchType
  pattern?: string
  priority?: number
  enabled?: boolean
  notes?: string | null
  chat_template?: string | null
}

export interface CompatibleEngine {
  engine: string
  device_architecture: DeviceArchitecture
  version: string
  container_image: string
  engine_version_id?: string
  engine_id?: string
  tool_calling_parser_type?: string | null
  reasoning_parser_type?: string | null
  architecture_family?: string | null
  chat_template?: string | null
  parser_source?: string | null
  parser_notes?: string | null
}

export interface EngineCompatibilityCreate {
  engine_version_id: string
  architectures: Record<string, any>
  features: Record<string, any>
}

export interface EngineCompatibilityUpdate {
  architectures?: Record<string, any>
  features?: Record<string, any>
}

// API Response Types
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ErrorResponse {
  message: string
  code: number
  details?: any
}

export interface SuccessResponse<T = any> {
  message: string
  code: number
  data?: T
}
