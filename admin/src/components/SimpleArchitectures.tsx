import { useState, useEffect } from 'react'
import { architectureApi } from '../api'
import { ModelArchitecture, ModelArchitectureCreate, ModelArchitectureUpdate } from '../types'

export function SimpleArchitectures() {
  const [architectures, setArchitectures] = useState<ModelArchitecture[]>([])
  const [loading, setLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingArchitecture, setEditingArchitecture] = useState<ModelArchitecture | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const [formData, setFormData] = useState<ModelArchitectureCreate>({
    class_name: '',
    architecture_family: '',
    tool_calling_parser_type: null,
    reasoning_parser_type: null,
    supports_lora: false,
    supports_pipeline_parallelism: false,
  })

  useEffect(() => {
    fetchArchitectures()
  }, [currentPage, searchTerm])

  const fetchArchitectures = async () => {
    try {
      setLoading(true)
      const params: any = {
        page: currentPage,
        page_size: 20
      }

      if (searchTerm) params.search = searchTerm

      const response = await architectureApi.getAll(params)
      setArchitectures(response.architectures)
      setTotalPages(Math.ceil(response.total / 20))
    } catch (error) {
      console.error('Failed to fetch architectures:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingArchitecture) {
        const updateData: ModelArchitectureUpdate = {
          architecture_family: formData.architecture_family,
          tool_calling_parser_type: formData.tool_calling_parser_type,
          reasoning_parser_type: formData.reasoning_parser_type,
          supports_lora: formData.supports_lora,
          supports_pipeline_parallelism: formData.supports_pipeline_parallelism,
        }
        await architectureApi.update(editingArchitecture.id, updateData)
      } else {
        await architectureApi.create(formData)
      }
      setShowEditModal(false)
      setEditingArchitecture(null)
      resetForm()
      fetchArchitectures()
    } catch (error) {
      console.error('Failed to save architecture:', error)
      alert('Failed to save architecture. Check if the class name is unique.')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this architecture?')) {
      try {
        await architectureApi.delete(id)
        fetchArchitectures()
      } catch (error) {
        console.error('Failed to delete architecture:', error)
        alert('Failed to delete architecture. It may be in use by models.')
      }
    }
  }

  const handleEdit = (architecture: ModelArchitecture) => {
    setEditingArchitecture(architecture)
    setFormData({
      class_name: architecture.class_name,
      architecture_family: architecture.architecture_family,
      tool_calling_parser_type: architecture.tool_calling_parser_type,
      reasoning_parser_type: architecture.reasoning_parser_type,
      supports_lora: architecture.supports_lora,
      supports_pipeline_parallelism: architecture.supports_pipeline_parallelism,
    })
    setShowEditModal(true)
  }

  const resetForm = () => {
    setFormData({
      class_name: '',
      architecture_family: '',
      tool_calling_parser_type: null,
      reasoning_parser_type: null,
      supports_lora: false,
      supports_pipeline_parallelism: false,
    })
  }

  if (loading && architectures.length === 0) {
    return <div>Loading architectures...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Architecture Management</h1>
        <button
          onClick={() => {
            setEditingArchitecture(null)
            resetForm()
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
          Add Architecture
        </button>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search architectures by class name or family..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
      </div>

      {/* Architecture Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Class Name</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Family</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Tool Calling</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Reasoning</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Models</th>
              <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {architectures.map((arch) => (
              <tr key={arch.id}>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee', fontFamily: 'monospace' }}>
                  {arch.class_name}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                  <span style={{
                    padding: '2px 6px',
                    backgroundColor: '#e9ecef',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    {arch.architecture_family}
                  </span>
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                  {arch.tool_calling_parser_type ? (
                    <span style={{
                      padding: '2px 6px',
                      backgroundColor: '#d1ecf1',
                      color: '#0c5460',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}>
                      {arch.tool_calling_parser_type}
                    </span>
                  ) : (
                    <span style={{ color: '#999' }}>-</span>
                  )}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                  {arch.reasoning_parser_type ? (
                    <span style={{
                      padding: '2px 6px',
                      backgroundColor: '#d4edda',
                      color: '#155724',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}>
                      {arch.reasoning_parser_type}
                    </span>
                  ) : (
                    <span style={{ color: '#999' }}>-</span>
                  )}
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                  <span style={{
                    padding: '2px 6px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '12px'
                  }}>
                    {arch.model_count || 0}
                  </span>
                </td>
                <td style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                  <button
                    onClick={() => handleEdit(arch)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      marginRight: '5px'
                    }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(arch.id)}
                    disabled={(arch.model_count ?? 0) > 0}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: (arch.model_count ?? 0) > 0 ? '#6c757d' : '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: (arch.model_count ?? 0) > 0 ? 'not-allowed' : 'pointer',
                      opacity: (arch.model_count ?? 0) > 0 ? 0.5 : 1
                    }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {architectures.length === 0 && (
          <div style={{ padding: '20px', textAlign: 'center' }}>No architectures found</div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '8px 16px',
              backgroundColor: currentPage === 1 ? '#e9ecef' : '#007bff',
              color: currentPage === 1 ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Previous
          </button>
          <span style={{ padding: '8px' }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '8px 16px',
              backgroundColor: currentPage === totalPages ? '#e9ecef' : '#007bff',
              color: currentPage === totalPages ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next
          </button>
        </div>
      )}

      {/* Edit Modal */}
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
            width: '500px'
          }}>
            <h2>{editingArchitecture ? 'Edit Architecture' : 'Add New Architecture'}</h2>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Class Name *
                </label>
                <input
                  type="text"
                  value={formData.class_name}
                  onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                  required
                  disabled={!!editingArchitecture}
                  placeholder="e.g., LlamaForCausalLM"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: editingArchitecture ? '#f8f9fa' : 'white'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Architecture Family *
                </label>
                <input
                  type="text"
                  value={formData.architecture_family}
                  onChange={(e) => setFormData({ ...formData, architecture_family: e.target.value })}
                  required
                  placeholder="e.g., llama"
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
                  Tool Calling Template (optional)
                </label>
                <input
                  type="text"
                  value={formData.tool_calling_parser_type || ''}
                  onChange={(e) => setFormData({ ...formData, tool_calling_parser_type: e.target.value || null })}
                  placeholder="e.g., llama3_json"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
                <small style={{ color: '#666' }}>
                  Leave empty if this architecture doesn't support tool calling
                </small>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Reasoning Parser Type (optional)
                </label>
                <input
                  type="text"
                  value={formData.reasoning_parser_type || ''}
                  onChange={(e) => setFormData({ ...formData, reasoning_parser_type: e.target.value || null })}
                  placeholder="e.g., qwen3"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
                <small style={{ color: '#666' }}>
                  Leave empty if this architecture doesn't support reasoning outputs
                </small>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.supports_lora || false}
                    onChange={(e) => setFormData({ ...formData, supports_lora: e.target.checked })}
                    style={{ cursor: 'pointer' }}
                  />
                  <span>Supports LoRA</span>
                </label>
                <small style={{ color: '#666', marginLeft: '28px' }}>
                  Check if this architecture supports LoRA fine-tuning
                </small>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={formData.supports_pipeline_parallelism || false}
                    onChange={(e) => setFormData({ ...formData, supports_pipeline_parallelism: e.target.checked })}
                    style={{ cursor: 'pointer' }}
                  />
                  <span>Supports Pipeline Parallelism</span>
                </label>
                <small style={{ color: '#666', marginLeft: '28px' }}>
                  Check if this architecture supports pipeline parallelism
                </small>
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false)
                    setEditingArchitecture(null)
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
                  {editingArchitecture ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}