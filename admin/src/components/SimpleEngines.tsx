import { useState, useEffect } from 'react'
import { engineApi } from '../api'
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
  DeviceArchitecture 
} from '../types'

const DEVICE_ARCHITECTURES: DeviceArchitecture[] = ['CUDA', 'CPU', 'ROCM', 'HPU']

export function SimpleEngines() {
  const [engines, setEngines] = useState<Engine[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showVersionModal, setShowVersionModal] = useState(false)
  const [showCompatibilityModal, setShowCompatibilityModal] = useState(false)
  const [editingEngine, setEditingEngine] = useState<Engine | null>(null)
  const [selectedEngine, setSelectedEngine] = useState<Engine | null>(null)
  const [selectedVersion, setSelectedVersion] = useState<EngineVersion | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedEngines, setExpandedEngines] = useState<Set<string>>(new Set())
  const [engineVersions, setEngineVersions] = useState<Record<string, EngineVersion[]>>({})
  
  const [formData, setFormData] = useState<EngineCreate>({
    name: ''
  })

  const [versionFormData, setVersionFormData] = useState<EngineVersionCreate>({
    engine_id: '',
    version: '',
    container_image: '',
    device_architecture: 'CUDA'
  })

  const [compatibilityFormData, setCompatibilityFormData] = useState<EngineCompatibilityCreate>({
    engine_version_id: '',
    architectures: {},
    features: {}
  })

  useEffect(() => {
    fetchEngines()
  }, [searchTerm])

  const fetchEngines = async () => {
    try {
      setLoading(true)
      const params: any = { page: 1, page_size: 100 }
      if (searchTerm) params.search = searchTerm
      
      const response = await engineApi.getAll(params)
      setEngines(response.engines)
    } catch (error) {
      console.error('Failed to fetch engines:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchEngineVersions = async (engineId: string) => {
    try {
      const response = await engineApi.getVersions({ engine_id: engineId, page: 1, page_size: 100 })
      setEngineVersions(prev => ({ ...prev, [engineId]: response.versions }))
    } catch (error) {
      console.error('Failed to fetch engine versions:', error)
    }
  }

  const toggleEngineExpand = async (engineId: string) => {
    const newExpanded = new Set(expandedEngines)
    if (newExpanded.has(engineId)) {
      newExpanded.delete(engineId)
    } else {
      newExpanded.add(engineId)
      if (!engineVersions[engineId]) {
        await fetchEngineVersions(engineId)
      }
    }
    setExpandedEngines(newExpanded)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingEngine) {
        await engineApi.update(editingEngine.id, formData as EngineUpdate)
      } else {
        await engineApi.create(formData)
      }
      setShowAddModal(false)
      setEditingEngine(null)
      resetForm()
      fetchEngines()
    } catch (error) {
      console.error('Failed to save engine:', error)
      alert('Failed to save engine')
    }
  }

  const handleVersionSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await engineApi.createVersion(versionFormData)
      setShowVersionModal(false)
      setSelectedEngine(null)
      resetVersionForm()
      // Refresh versions for the engine
      if (versionFormData.engine_id) {
        await fetchEngineVersions(versionFormData.engine_id)
      }
    } catch (error) {
      console.error('Failed to create engine version:', error)
      alert('Failed to create engine version')
    }
  }

  const handleCompatibilitySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // Parse JSON strings to objects
      const architecturesObj = compatibilityFormData.architectures
      const featuresObj = compatibilityFormData.features

      await engineApi.createCompatibility({
        engine_version_id: compatibilityFormData.engine_version_id,
        architectures: architecturesObj,
        features: featuresObj
      })
      
      setShowCompatibilityModal(false)
      setSelectedVersion(null)
      resetCompatibilityForm()
      // Refresh the engine versions
      if (selectedEngine) {
        await fetchEngineVersions(selectedEngine.id)
      }
    } catch (error) {
      console.error('Failed to create compatibility:', error)
      alert('Failed to create compatibility. Please check your JSON format.')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this engine?')) {
      try {
        await engineApi.delete(id)
        fetchEngines()
      } catch (error) {
        console.error('Failed to delete engine:', error)
        alert('Failed to delete engine')
      }
    }
  }

  const handleDeleteVersion = async (versionId: string, engineId: string) => {
    if (window.confirm('Are you sure you want to delete this version?')) {
      try {
        await engineApi.deleteVersion(versionId)
        await fetchEngineVersions(engineId)
      } catch (error) {
        console.error('Failed to delete version:', error)
        alert('Failed to delete version')
      }
    }
  }

  const handleEdit = (engine: Engine) => {
    setEditingEngine(engine)
    setFormData({
      name: engine.name
    })
    setShowAddModal(true)
  }

  const handleAddVersion = (engine: Engine) => {
    setSelectedEngine(engine)
    setVersionFormData({
      engine_id: engine.id,
      version: '',
      container_image: '',
      device_architecture: 'CUDA'
    })
    setShowVersionModal(true)
  }

  const handleAddCompatibility = (version: EngineVersion, engine: Engine) => {
    setSelectedEngine(engine)
    setSelectedVersion(version)
    setCompatibilityFormData({
      engine_version_id: version.id,
      architectures: {},
      features: {}
    })
    setShowCompatibilityModal(true)
  }

  const resetForm = () => {
    setFormData({
      name: ''
    })
  }

  const resetVersionForm = () => {
    setVersionFormData({
      engine_id: '',
      version: '',
      container_image: '',
      device_architecture: 'CUDA'
    })
  }

  const resetCompatibilityForm = () => {
    setCompatibilityFormData({
      engine_version_id: '',
      architectures: {},
      features: {}
    })
  }

  if (loading) {
    return <div>Loading engines...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Engines</h1>
        <button
          onClick={() => {
            setEditingEngine(null)
            resetForm()
            setShowAddModal(true)
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
          Add Engine
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search engines..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
      </div>

      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        {engines.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>No engines found</div>
        ) : (
          engines.map((engine) => (
            <div key={engine.id} style={{ borderBottom: '1px solid #eee' }}>
              <div style={{ 
                padding: '15px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backgroundColor: expandedEngines.has(engine.id) ? '#f8f9fa' : 'white'
              }}>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0, marginBottom: '5px' }}>{engine.name}</h3>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    ID: {engine.id}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={() => toggleEngineExpand(engine.id)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#f0f0f0',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    {expandedEngines.has(engine.id) ? 'Collapse' : 'Expand'}
                  </button>
                  <button
                    onClick={() => handleAddVersion(engine)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Add Version
                  </button>
                  <button
                    onClick={() => handleEdit(engine)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#ffc107',
                      color: 'black',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(engine.id)}
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
              
              {expandedEngines.has(engine.id) && engineVersions[engine.id] && (
                <div style={{ padding: '0 15px 15px 15px' }}>
                  <h4>Versions:</h4>
                  {engineVersions[engine.id].length === 0 ? (
                    <div style={{ padding: '10px', color: '#666' }}>No versions found</div>
                  ) : (
                    engineVersions[engine.id].map((version) => (
                      <div key={version.id} style={{
                        padding: '10px',
                        marginBottom: '10px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px',
                        border: '1px solid #e9ecef'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <strong>Version:</strong> {version.version}<br />
                            <strong>Architecture:</strong> {version.device_architecture}<br />
                            <strong>Container:</strong> {version.container_image}
                          </div>
                          <div style={{ display: 'flex', gap: '5px' }}>
                            <button
                              onClick={() => handleAddCompatibility(version, engine)}
                              style={{
                                padding: '3px 8px',
                                backgroundColor: '#17a2b8',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Add Compatibility
                            </button>
                            <button
                              onClick={() => handleDeleteVersion(version.id, engine.id)}
                              style={{
                                padding: '3px 8px',
                                backgroundColor: '#dc3545',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px'
                              }}
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Add/Edit Engine Modal */}
      {showAddModal && (
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
            width: '500px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h2>{editingEngine ? 'Edit Engine' : 'Add New Engine'}</h2>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false)
                    setEditingEngine(null)
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
                  {editingEngine ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Version Modal */}
      {showVersionModal && (
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
            width: '500px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h2>Add Engine Version</h2>
            <p>For engine: <strong>{selectedEngine?.name}</strong></p>
            <form onSubmit={handleVersionSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Version *
                </label>
                <input
                  type="text"
                  value={versionFormData.version}
                  onChange={(e) => setVersionFormData({ ...versionFormData, version: e.target.value })}
                  required
                  placeholder="e.g., 0.7.25"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Container Image *
                </label>
                <input
                  type="text"
                  value={versionFormData.container_image}
                  onChange={(e) => setVersionFormData({ ...versionFormData, container_image: e.target.value })}
                  required
                  placeholder="e.g., budecosystem/vllm:0.7.25"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Device Architecture *
                </label>
                <select
                  value={versionFormData.device_architecture}
                  onChange={(e) => setVersionFormData({ ...versionFormData, device_architecture: e.target.value as DeviceArchitecture })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                >
                  {DEVICE_ARCHITECTURES.map(arch => (
                    <option key={arch} value={arch}>{arch}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowVersionModal(false)
                    setSelectedEngine(null)
                    resetVersionForm()
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
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Compatibility Modal */}
      {showCompatibilityModal && (
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
            width: '600px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h2>Add Engine Compatibility</h2>
            <p>For version: <strong>{selectedVersion?.version}</strong> ({selectedVersion?.device_architecture})</p>
            <form onSubmit={handleCompatibilitySubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Architectures (JSON) *
                </label>
                <textarea
                  value={JSON.stringify(compatibilityFormData.architectures, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      setCompatibilityFormData({ ...compatibilityFormData, architectures: parsed })
                    } catch {
                      // Keep the text as is if it's not valid JSON yet
                      setCompatibilityFormData({ ...compatibilityFormData, architectures: e.target.value as any })
                    }
                  }}
                  required
                  placeholder='{"model_architectures": ["transformers", "llama"]}'
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    minHeight: '100px',
                    fontFamily: 'monospace'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Features (JSON) *
                </label>
                <textarea
                  value={JSON.stringify(compatibilityFormData.features, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value)
                      setCompatibilityFormData({ ...compatibilityFormData, features: parsed })
                    } catch {
                      // Keep the text as is if it's not valid JSON yet
                      setCompatibilityFormData({ ...compatibilityFormData, features: e.target.value as any })
                    }
                  }}
                  required
                  placeholder='{"supports_streaming": true, "supports_batching": true}'
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    minHeight: '100px',
                    fontFamily: 'monospace'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowCompatibilityModal(false)
                    setSelectedVersion(null)
                    resetCompatibilityForm()
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
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}