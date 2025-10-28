import { useState, useEffect } from 'react'
import { modelApi, licenseApi, providerApi, architectureApi } from '../api'
import { Model, ModelCreate, ModelUpdate, License, Provider, ModalityEnum, ModelEndpointEnum, ModelArchitecture } from '../types'

const MODALITY_OPTIONS: ModalityEnum[] = ['text_input', 'text_output', 'image_input', 'image_output', 'audio_input', 'audio_output']
const ENDPOINT_OPTIONS: ModelEndpointEnum[] = [
  '/v1/chat/completions',
  '/v1/completions',
  '/v1/images/generations',
  '/v1/images/edits',
  '/v1/images/variations',
  '/v1/audio/transcriptions',
  '/v1/audio/translations',
  '/v1/audio/speech',
  '/v1/embeddings',
  '/v1/batch',
  '/v1/responses',
  '/v1/documents',
  '/v1/rerank',
  '/v1/moderations'
]

export function SimpleModels() {
  const [models, setModels] = useState<Model[]>([])
  const [licenses, setLicenses] = useState<License[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [architectures, setArchitectures] = useState<ModelArchitecture[]>([])
  const [loading, setLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingModel, setEditingModel] = useState<Model | null>(null)
  const [expandedModels, setExpandedModels] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [filterProvider, setFilterProvider] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [activeTab, setActiveTab] = useState<'basic' | 'details' | 'pricing' | 'features'>('basic')
  
  const [formData, setFormData] = useState<ModelCreate & {
    model_architecture_class_id?: string
    chat_template?: string
    tool_calling_parser_type?: string
    description?: string
    advantages?: string[]
    disadvantages?: string[]
    use_cases?: string[]
    languages?: string[]
    tags?: string[]
    tasks?: string[]
    github_url?: string
    website_url?: string
    logo_url?: string
  }>({
    uri: '',
    modality: [],
    provider_id: '',
    endpoints: [],
    license_id: undefined,
    model_architecture_class_id: undefined,
    chat_template: undefined,
    tool_calling_parser_type: undefined,
    input_cost: {},
    output_cost: {},
    cache_cost: {},
    tokens: {},
    rate_limits: {},
    media_limits: {},
    features: {},
    description: '',
    advantages: [],
    disadvantages: [],
    use_cases: [],
    languages: [],
    tags: [],
    tasks: [],
    github_url: '',
    website_url: '',
    logo_url: ''
  })

  useEffect(() => {
    fetchModels()
    fetchLicenses()
    fetchProviders()
    fetchArchitectures()
  }, [currentPage, searchTerm, filterProvider])

  const fetchModels = async () => {
    try {
      setLoading(true)
      const params: any = { 
        page: currentPage, 
        page_size: 20
      }
      
      if (searchTerm) params.search = searchTerm
      if (filterProvider) params.provider_id = filterProvider
      
      const response = await modelApi.getAll(params)
      // Models are now sorted by created_at on the backend (newest first)
      setModels(response.models)
      setTotalPages(Math.ceil(response.total / 20))
    } catch (error) {
      console.error('Failed to fetch models:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchLicenses = async () => {
    try {
      const response = await licenseApi.getAll({ page: 1, page_size: 500 })
      // Sort licenses alphabetically by name (create a copy to avoid mutation)
      const sortedLicenses = [...response.licenses].sort((a, b) => 
        a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
      )
      setLicenses(sortedLicenses)
    } catch (error) {
      console.error('Failed to fetch licenses:', error)
    }
  }

  const fetchProviders = async () => {
    try {
      const response = await providerApi.getAll({ page: 1, page_size: 500 })
      // Sort providers alphabetically by name (create a copy to avoid mutation)
      const sortedProviders = [...response.providers].sort((a, b) =>
        a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
      )
      setProviders(sortedProviders)
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    }
  }

  const fetchArchitectures = async () => {
    try {
      const response = await architectureApi.getAll({ page: 1, page_size: 500 })
      // Sort architectures alphabetically by class name
      const sortedArchitectures = [...response.architectures].sort((a, b) =>
        a.class_name.localeCompare(b.class_name, undefined, { sensitivity: 'base' })
      )
      setArchitectures(sortedArchitectures)
    } catch (error) {
      console.error('Failed to fetch architectures:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // Clean up empty objects
      const cleanData: any = {
        uri: formData.uri,
        modality: formData.modality,
        provider_id: formData.provider_id,
        endpoints: formData.endpoints,
        license_id: formData.license_id || undefined,
        model_architecture_class_id: formData.model_architecture_class_id || undefined,
        chat_template: formData.chat_template || undefined,
        tool_calling_parser_type: formData.tool_calling_parser_type || undefined,
        input_cost: Object.keys(formData.input_cost || {}).length > 0 ? formData.input_cost : undefined,
        output_cost: Object.keys(formData.output_cost || {}).length > 0 ? formData.output_cost : undefined,
        cache_cost: Object.keys(formData.cache_cost || {}).length > 0 ? formData.cache_cost : undefined,
        tokens: Object.keys(formData.tokens || {}).length > 0 ? formData.tokens : undefined,
        rate_limits: Object.keys(formData.rate_limits || {}).length > 0 ? formData.rate_limits : undefined,
        media_limits: Object.keys(formData.media_limits || {}).length > 0 ? formData.media_limits : undefined,
        features: Object.keys(formData.features || {}).length > 0 ? formData.features : undefined
      }

      if (editingModel) {
        await modelApi.update(editingModel.id, cleanData)
        
        // Save model details
        const detailsData = {
          description: formData.description,
          advantages: formData.advantages,
          disadvantages: formData.disadvantages,
          use_cases: formData.use_cases,
          tags: formData.tags,
          // Include pricing and features from formData
          input_cost: formData.input_cost,
          output_cost: formData.output_cost,
          cache_cost: formData.cache_cost,
          search_context_cost_per_query: formData.search_context_cost_per_query,
          tokens: formData.tokens,
          rate_limits: formData.rate_limits,
          media_limits: formData.media_limits,
          features: formData.features
        }
        
        await modelApi.updateModelDetails(editingModel.id, detailsData)
      } else {
        await modelApi.create(cleanData)
      }
      setShowEditModal(false)
      setEditingModel(null)
      resetForm()
      fetchModels()
    } catch (error) {
      console.error('Failed to save model:', error)
      alert('Failed to save model. Check if the URI is unique.')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this model?')) {
      try {
        await modelApi.delete(id)
        fetchModels()
      } catch (error) {
        console.error('Failed to delete model:', error)
        alert('Failed to delete model.')
      }
    }
  }

  const handleEdit = async (model: Model) => {
    setEditingModel(model)
    setFormData({
      uri: model.uri,
      modality: model.modality || [],
      provider_id: model.provider_id,
      endpoints: model.endpoints || [],
      license_id: model.license?.id,
      model_architecture_class_id: model.architecture_class?.id,
      chat_template: model.chat_template,
      tool_calling_parser_type: model.tool_calling_parser_type || undefined,
      input_cost: model.input_cost || {},
      output_cost: model.output_cost || {},
      cache_cost: model.cache_cost || {},
      tokens: model.tokens || {},
      rate_limits: model.rate_limits || {},
      media_limits: model.media_limits || {},
      features: model.features || {},
      description: '',
      advantages: [],
      disadvantages: [],
      use_cases: [],
      languages: [],
      tags: [],
      tasks: [],
      github_url: '',
      website_url: '',
      logo_url: ''
    })
    
    // Try to fetch model details
    try {
      const details = await modelApi.getModelDetails(model.uri)
      if (details) {
        setFormData(prev => ({
          ...prev,
          description: details.description || '',
          advantages: details.advantages || [],
          disadvantages: details.disadvantages || [],
          use_cases: details.use_cases || [],
          languages: details.languages || [],
          tags: details.tags || [],
          tasks: details.tasks || [],
          github_url: details.github_url || '',
          website_url: details.website_url || '',
          logo_url: details.logo_url || '',
          tool_calling_parser_type: details.tool_calling_parser_type ?? prev.tool_calling_parser_type
        }))
      }
    } catch (error) {
      console.error('Failed to fetch model details:', error)
    }
    
    setActiveTab('basic')
    setShowEditModal(true)
  }

  const toggleExpand = (modelId: string) => {
    const newExpanded = new Set(expandedModels)
    if (newExpanded.has(modelId)) {
      newExpanded.delete(modelId)
    } else {
      newExpanded.add(modelId)
    }
    setExpandedModels(newExpanded)
  }

  const resetForm = () => {
    setFormData({
      uri: '',
      modality: [],
      provider_id: '',
      endpoints: [],
      license_id: undefined,
      model_architecture_class_id: undefined,
      chat_template: undefined,
      tool_calling_parser_type: undefined,
      input_cost: {},
      output_cost: {},
      cache_cost: {},
      tokens: {},
      rate_limits: {},
      media_limits: {},
      features: {},
      description: '',
      advantages: [],
      disadvantages: [],
      use_cases: [],
      languages: [],
      tags: [],
      tasks: [],
      github_url: '',
      website_url: '',
      logo_url: ''
    })
  }

  const addToArray = (field: 'advantages' | 'disadvantages' | 'use_cases' | 'tags' | 'languages' | 'tasks', value: string) => {
    if (value && Array.isArray(formData[field])) {
      setFormData({
        ...formData,
        [field]: [...formData[field], value]
      })
    }
  }

  const removeFromArray = (field: 'advantages' | 'disadvantages' | 'use_cases' | 'tags' | 'languages' | 'tasks', index: number) => {
    if (Array.isArray(formData[field])) {
      setFormData({
        ...formData,
        [field]: formData[field].filter((_, i) => i !== index)
      })
    }
  }

  const getLicenseBadgeColor = (suitability?: string) => {
    switch (suitability) {
      case 'MOST': return '#28a745'
      case 'GOOD': return '#17a2b8'
      case 'LOW': return '#ffc107'
      case 'WORST': return '#dc3545'
      default: return '#6c757d'
    }
  }

  if (loading && models.length === 0) {
    return <div>Loading models...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Model Management</h1>
        <button
          onClick={() => {
            setEditingModel(null)
            resetForm()
            setActiveTab('basic')
            setShowEditModal(true)
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add Model
        </button>
      </div>

      {/* Filters */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search models by URI..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
        <select
          value={filterProvider}
          onChange={(e) => {
            setFilterProvider(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Providers</option>
          {providers.map(provider => (
            <option key={provider.id} value={provider.id}>{provider.name}</option>
          ))}
        </select>
      </div>

      {/* Model List */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        {models.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>No models found</div>
        ) : (
          models.map((model) => (
            <div key={model.id} style={{ borderBottom: '1px solid #eee' }}>
              <div style={{ 
                padding: '15px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                backgroundColor: expandedModels.has(model.id) ? '#f8f9fa' : 'white'
              }}
              onClick={() => toggleExpand(model.id)}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                    <h3 style={{ margin: 0 }}>{model.uri}</h3>
                    {model.license && (
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: getLicenseBadgeColor(model.license.type_suitability),
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {model.license.name} ({model.license.type_suitability})
                      </span>
                    )}
                    {!model.license && (
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        fontSize: '12px'
                      }}>
                        No License
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Provider:</strong> {model.provider_name || 'Unknown'} |
                    <strong> Modality:</strong> {model.modality?.join(', ') || 'N/A'} |
                    <strong> Architecture:</strong> {model.architecture_class?.architecture_family || 'N/A'} |
                    <strong> Added:</strong> {model.created_at ? new Date(model.created_at).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEdit(model)
                    }}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(model.id)
                    }}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
              
              {expandedModels.has(model.id) && (
                <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderTop: '1px solid #e9ecef' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div>
                      <h4>Model Information:</h4>
                      <p><strong>ID:</strong> {model.id}</p>
                      <p><strong>Provider Type:</strong> {model.provider_type || 'N/A'}</p>
                      {model.tool_calling_parser_type && (
                        <p><strong>Tool Calling Parser (Model):</strong> {model.tool_calling_parser_type}</p>
                      )}
                      {model.architecture_class && (
                        <>
                          <p><strong>Architecture Class:</strong> {model.architecture_class.class_name}</p>
                          <p><strong>Architecture Family:</strong> {model.architecture_class.architecture_family}</p>
                          {model.architecture_class.tool_calling_parser_type && (
                            <p><strong>Tool Calling (Architecture):</strong> {model.architecture_class.tool_calling_parser_type}</p>
                          )}
                          {model.architecture_class.reasoning_parser_type && (
                            <p><strong>Reasoning Parser:</strong> {model.architecture_class.reasoning_parser_type}</p>
                          )}
                        </>
                      )}
                      {model.deprecation_date && (
                        <p><strong>Deprecation Date:</strong> {new Date(model.deprecation_date).toLocaleDateString()}</p>
                      )}
                      {model.chat_template && (
                        <div>
                          <p><strong>Chat Template:</strong></p>
                          <pre style={{
                            backgroundColor: '#f4f4f4',
                            padding: '8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            overflow: 'auto',
                            maxHeight: '150px'
                          }}>
                            {model.chat_template}
                          </pre>
                        </div>
                      )}
                    </div>
                    <div>
                      <h4>Endpoints:</h4>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                        {model.endpoints?.map((endpoint, idx) => (
                          <li key={idx}>{endpoint}</li>
                        )) || <li>No endpoints</li>}
                      </ul>
                    </div>
                    {model.tokens && Object.keys(model.tokens).length > 0 && (
                      <div>
                        <h4>Token Limits:</h4>
                        <pre style={{ fontSize: '12px', backgroundColor: 'white', padding: '5px', borderRadius: '3px' }}>
                          {JSON.stringify(model.tokens, null, 2)}
                        </pre>
                      </div>
                    )}
                    {model.features && Object.keys(model.features).length > 0 && (
                      <div>
                        <h4>Features:</h4>
                        <pre style={{ fontSize: '12px', backgroundColor: 'white', padding: '5px', borderRadius: '3px' }}>
                          {JSON.stringify(model.features, null, 2)}
                        </pre>
                      </div>
                    )}
                    {(model.input_cost && Object.keys(model.input_cost).length > 0) && (
                      <div>
                        <h4>Input Cost:</h4>
                        <pre style={{ fontSize: '12px', backgroundColor: 'white', padding: '5px', borderRadius: '3px' }}>
                          {JSON.stringify(model.input_cost, null, 2)}
                        </pre>
                      </div>
                    )}
                    {(model.output_cost && Object.keys(model.output_cost).length > 0) && (
                      <div>
                        <h4>Output Cost:</h4>
                        <pre style={{ fontSize: '12px', backgroundColor: 'white', padding: '5px', borderRadius: '3px' }}>
                          {JSON.stringify(model.output_cost, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '5px 10px',
              backgroundColor: currentPage === 1 ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Previous
          </button>
          <span style={{ padding: '5px 10px' }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '5px 10px',
              backgroundColor: currentPage === totalPages ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next
          </button>
        </div>
      )}

      {/* Combined Edit/Details Modal with Tabs */}
      {showEditModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            width: '900px',
            maxHeight: '85vh',
            overflow: 'auto'
          }}>
            <h2>{editingModel ? 'Edit Model' : 'Add New Model'}</h2>
            
            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #e9ecef' }}>
              <button
                type="button"
                onClick={() => setActiveTab('basic')}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderBottom: activeTab === 'basic' ? '2px solid #007bff' : 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === 'basic' ? '#007bff' : '#666',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'basic' ? 'bold' : 'normal'
                }}
              >
                Basic Info
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('details')}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderBottom: activeTab === 'details' ? '2px solid #007bff' : 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === 'details' ? '#007bff' : '#666',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'details' ? 'bold' : 'normal'
                }}
              >
                Details
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('pricing')}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderBottom: activeTab === 'pricing' ? '2px solid #007bff' : 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === 'pricing' ? '#007bff' : '#666',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'pricing' ? 'bold' : 'normal'
                }}
              >
                Pricing & Limits
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('features')}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderBottom: activeTab === 'features' ? '2px solid #007bff' : 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === 'features' ? '#007bff' : '#666',
                  cursor: 'pointer',
                  fontWeight: activeTab === 'features' ? 'bold' : 'normal'
                }}
              >
                Features
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {/* Basic Info Tab */}
              {activeTab === 'basic' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      URI * (e.g., "openai/gpt-4")
                    </label>
                    <input
                      type="text"
                      value={formData.uri}
                      onChange={(e) => setFormData({ ...formData, uri: e.target.value })}
                      required
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Provider *
                    </label>
                    <select
                      value={formData.provider_id}
                      onChange={(e) => setFormData({ ...formData, provider_id: e.target.value })}
                      required
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Provider</option>
                      {providers.map(provider => (
                        <option key={provider.id} value={provider.id}>{provider.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      License
                    </label>
                    <select
                      value={formData.license_id || ''}
                      onChange={(e) => setFormData({ ...formData, license_id: e.target.value || undefined })}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">No License</option>
                      {licenses.map(license => (
                        <option key={license.id} value={license.id}>
                          {license.name} ({license.type_suitability})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Architecture Class
                    </label>
                    <select
                      value={formData.model_architecture_class_id || ''}
                      onChange={(e) => setFormData({ ...formData, model_architecture_class_id: e.target.value || undefined })}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Architecture</option>
                      {architectures.map(arch => (
                        <option key={arch.id} value={arch.id}>
                          {arch.class_name} ({arch.architecture_family})
                        </option>
                      ))}
                    </select>
                    {formData.model_architecture_class_id && (() => {
                      const selectedArch = architectures.find(a => a.id === formData.model_architecture_class_id)
                      return selectedArch ? (
                        <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                          {selectedArch.tool_calling_parser_type && (
                            <div>Tool Calling: {selectedArch.tool_calling_parser_type}</div>
                          )}
                          {selectedArch.reasoning_parser_type && (
                            <div>Reasoning: {selectedArch.reasoning_parser_type}</div>
                          )}
                          {formData.tool_calling_parser_type && (
                            <div>Model Override: {formData.tool_calling_parser_type}</div>
                          )}
                          {!selectedArch.tool_calling_parser_type && !selectedArch.reasoning_parser_type && (
                            <div>No special capabilities</div>
                          )}
                        </div>
                      ) : null
                    })()}
                  </div>

                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Modality * (select multiple)
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                      {MODALITY_OPTIONS.map(mod => (
                        <label key={mod} style={{ display: 'flex', alignItems: 'center' }}>
                          <input
                            type="checkbox"
                            checked={formData.modality.includes(mod)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData({ ...formData, modality: [...formData.modality, mod] })
                              } else {
                                setFormData({ ...formData, modality: formData.modality.filter(m => m !== mod) })
                              }
                            }}
                            style={{ marginRight: '5px' }}
                          />
                          {mod}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Endpoints * (select multiple)
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                      {ENDPOINT_OPTIONS.map(endpoint => (
                        <label key={endpoint} style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
                          <input
                            type="checkbox"
                            checked={formData.endpoints.includes(endpoint)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData({ ...formData, endpoints: [...formData.endpoints, endpoint] })
                              } else {
                                setFormData({ ...formData, endpoints: formData.endpoints.filter(e => e !== endpoint) })
                              }
                            }}
                            style={{ marginRight: '5px' }}
                          />
                          {endpoint}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Chat Template (Jinja2 format)
                    </label>
                    <textarea
                      value={formData.chat_template || ''}
                      onChange={(e) => setFormData({ ...formData, chat_template: e.target.value || undefined })}
                      placeholder="Enter chat template in Jinja2 format..."
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        minHeight: '100px',
                        fontFamily: 'monospace',
                        fontSize: '12px'
                      }}
                    />
                  </div>
                  <div style={{ gridColumn: 'span 2' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Tool Calling Parser Type
                    </label>
                    <input
                      type="text"
                      value={formData.tool_calling_parser_type || ''}
                      onChange={(e) => setFormData({ ...formData, tool_calling_parser_type: e.target.value || undefined })}
                      placeholder="Enter parser type override (optional)"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Details Tab */}
              {activeTab === 'details' && (
                <div>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    {/* Advantages */}
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>Advantages</label>
                      <div style={{ display: 'flex', gap: '5px', marginBottom: '5px' }}>
                        <input
                          type="text"
                          placeholder="Add advantage..."
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              const input = e.target as HTMLInputElement
                              addToArray('advantages', input.value)
                              input.value = ''
                            }
                          }}
                          style={{
                            flex: 1,
                            padding: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '3px'
                          }}
                        />
                      </div>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px', maxHeight: '100px', overflow: 'auto' }}>
                        {formData.advantages?.map((adv, idx) => (
                          <li key={idx}>
                            {adv}
                            <button
                              type="button"
                              onClick={() => removeFromArray('advantages', idx)}
                              style={{
                                marginLeft: '10px',
                                padding: '2px 6px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '3px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Remove
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Disadvantages */}
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>Disadvantages</label>
                      <div style={{ display: 'flex', gap: '5px', marginBottom: '5px' }}>
                        <input
                          type="text"
                          placeholder="Add disadvantage..."
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              const input = e.target as HTMLInputElement
                              addToArray('disadvantages', input.value)
                              input.value = ''
                            }
                          }}
                          style={{
                            flex: 1,
                            padding: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '3px'
                          }}
                        />
                      </div>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px', maxHeight: '100px', overflow: 'auto' }}>
                        {formData.disadvantages?.map((dis, idx) => (
                          <li key={idx}>
                            {dis}
                            <button
                              type="button"
                              onClick={() => removeFromArray('disadvantages', idx)}
                              style={{
                                marginLeft: '10px',
                                padding: '2px 6px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '3px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Remove
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Use Cases */}
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>Use Cases</label>
                      <div style={{ display: 'flex', gap: '5px', marginBottom: '5px' }}>
                        <input
                          type="text"
                          placeholder="Add use case..."
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              const input = e.target as HTMLInputElement
                              addToArray('use_cases', input.value)
                              input.value = ''
                            }
                          }}
                          style={{
                            flex: 1,
                            padding: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '3px'
                          }}
                        />
                      </div>
                      <ul style={{ margin: '5px 0', paddingLeft: '20px', maxHeight: '100px', overflow: 'auto' }}>
                        {formData.use_cases?.map((use, idx) => (
                          <li key={idx}>
                            {use}
                            <button
                              type="button"
                              onClick={() => removeFromArray('use_cases', idx)}
                              style={{
                                marginLeft: '10px',
                                padding: '2px 6px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '3px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Remove
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Tags */}
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>Tags</label>
                      <div style={{ display: 'flex', gap: '5px', marginBottom: '5px' }}>
                        <input
                          type="text"
                          placeholder="Add tag..."
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              const input = e.target as HTMLInputElement
                              addToArray('tags', input.value)
                              input.value = ''
                            }
                          }}
                          style={{
                            flex: 1,
                            padding: '5px',
                            border: '1px solid #ddd',
                            borderRadius: '3px'
                          }}
                        />
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                        {formData.tags?.map((tag, idx) => (
                          <span key={idx} style={{
                            padding: '3px 8px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            borderRadius: '3px',
                            fontSize: '12px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '5px'
                          }}>
                            {tag}
                            <button
                              type="button"
                              onClick={() => removeFromArray('tags', idx)}
                              style={{
                                background: 'none',
                                border: 'none',
                                color: 'white',
                                cursor: 'pointer',
                                padding: 0,
                                fontSize: '14px'
                              }}
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div style={{ marginTop: '15px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>GitHub URL</label>
                      <input
                        type="url"
                        value={formData.github_url}
                        onChange={(e) => setFormData({ ...formData, github_url: e.target.value })}
                        style={{
                          width: '100%',
                          padding: '8px',
                          border: '1px solid #ddd',
                          borderRadius: '4px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '5px' }}>Website URL</label>
                      <input
                        type="url"
                        value={formData.website_url}
                        onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                        style={{
                          width: '100%',
                          padding: '8px',
                          border: '1px solid #ddd',
                          borderRadius: '4px'
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Pricing & Limits Tab */}
              {activeTab === 'pricing' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Input Cost per Token
                    </label>
                    <input
                      type="number"
                      step="0.000001"
                      value={formData.input_cost?.input_cost_per_token || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        input_cost: { ...formData.input_cost, input_cost_per_token: e.target.value ? parseFloat(e.target.value) : undefined }
                      })}
                      placeholder="0.00001"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Output Cost per Token
                    </label>
                    <input
                      type="number"
                      step="0.000001"
                      value={formData.output_cost?.output_cost_per_token || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        output_cost: { ...formData.output_cost, output_cost_per_token: e.target.value ? parseFloat(e.target.value) : undefined }
                      })}
                      placeholder="0.00002"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Max Input Tokens
                    </label>
                    <input
                      type="number"
                      value={formData.tokens?.max_input_tokens || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        tokens: { ...formData.tokens, max_input_tokens: e.target.value ? parseInt(e.target.value) : undefined }
                      })}
                      placeholder="128000"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      Max Output Tokens
                    </label>
                    <input
                      type="number"
                      value={formData.tokens?.max_output_tokens || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        tokens: { ...formData.tokens, max_output_tokens: e.target.value ? parseInt(e.target.value) : undefined }
                      })}
                      placeholder="4096"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      RPM (Requests per Minute)
                    </label>
                    <input
                      type="number"
                      value={formData.rate_limits?.rpm || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        rate_limits: { ...formData.rate_limits, rpm: e.target.value ? parseInt(e.target.value) : undefined }
                      })}
                      placeholder="1000"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '5px' }}>
                      TPM (Tokens per Minute)
                    </label>
                    <input
                      type="number"
                      value={formData.rate_limits?.tpm || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        rate_limits: { ...formData.rate_limits, tpm: e.target.value ? parseInt(e.target.value) : undefined }
                      })}
                      placeholder="150000"
                      style={{
                        width: '100%',
                        padding: '8px',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Features Tab */}
              {activeTab === 'features' && (
                <div>
                  <label style={{ display: 'block', marginBottom: '10px' }}>
                    Model Features
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px' }}>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_function_calling || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_function_calling: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Function Calling</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_native_streaming || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_native_streaming: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Native Streaming</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_web_search || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_web_search: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Web Search</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_reasoning || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_reasoning: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Reasoning</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_response_schema || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_response_schema: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Response Schema</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_system_messages || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_system_messages: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>System Messages</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_tool_choice || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_tool_choice: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Tool Choice</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_parallel_function_calling || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_parallel_function_calling: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Parallel Function Calling</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_assistant_prefill || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_assistant_prefill: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Assistant Prefill</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={formData.features?.supports_prompt_caching || false}
                        onChange={(e) => setFormData({
                          ...formData,
                          features: { ...formData.features, supports_prompt_caching: e.target.checked }
                        })}
                      />
                      <span style={{ marginLeft: '5px' }}>Prompt Caching</span>
                    </label>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false)
                    setEditingModel(null)
                    resetForm()
                  }}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {editingModel ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
