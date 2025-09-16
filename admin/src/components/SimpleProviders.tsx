import { useState, useEffect } from 'react'
import { providerApi } from '../api'
import { Provider, ProviderCreate, CredentialField } from '../types'

export function SimpleProviders() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [formData, setFormData] = useState<ProviderCreate>({
    name: '',
    provider_type: '',
    icon: 'icons/providers/default.png',
    description: '',
    credentials: []
  })

  useEffect(() => {
    fetchProviders()
  }, [])

  const fetchProviders = async () => {
    try {
      setLoading(true)
      const response = await providerApi.getAll()
      setProviders(response.providers)
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingProvider) {
        await providerApi.update(editingProvider.id, formData)
      } else {
        await providerApi.create(formData)
      }
      setShowAddModal(false)
      setEditingProvider(null)
      resetForm()
      fetchProviders()
    } catch (error) {
      console.error('Failed to save provider:', error)
      alert('Failed to save provider. Check if provider_type is unique.')
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this provider?')) {
      try {
        await providerApi.delete(id)
        fetchProviders()
      } catch (error: any) {
        console.error('Failed to delete provider:', error)
        // The error message from the backend is properly set by the API client interceptor
        const errorMessage = error.message || 'Failed to delete provider'
        alert(errorMessage)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      provider_type: '',
      icon: 'icons/providers/default.png',
      description: '',
      credentials: []
    })
  }

  const addCredentialField = () => {
    setFormData({
      ...formData,
      credentials: [
        ...formData.credentials,
        {
          field: '',
          label: '',
          type: 'text',
          description: '',
          required: true,
          order: formData.credentials.length + 1
        }
      ]
    })
  }

  const updateCredentialField = (index: number, field: Partial<CredentialField>) => {
    const updatedCredentials = [...formData.credentials]
    updatedCredentials[index] = { ...updatedCredentials[index], ...field }
    setFormData({ ...formData, credentials: updatedCredentials })
  }

  const removeCredentialField = (index: number) => {
    setFormData({
      ...formData,
      credentials: formData.credentials.filter((_, i) => i !== index)
    })
  }

  const openEditModal = (provider: Provider) => {
    setEditingProvider(provider)
    setFormData({
      name: provider.name,
      provider_type: provider.provider_type,
      icon: provider.icon,
      description: provider.description,
      credentials: provider.credentials
    })
    setShowAddModal(true)
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Provider Management</h2>
        <button
          onClick={() => {
            resetForm()
            setEditingProvider(null)
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
          + Add Provider
        </button>
      </div>

      {loading ? (
        <p>Loading providers...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {providers.map(provider => (
            <div
              key={provider.id}
              style={{
                padding: '20px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                backgroundColor: 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <h3>{provider.name}</h3>
                <span style={{
                  padding: '4px 8px',
                  backgroundColor: '#e9ecef',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}>
                  {provider.provider_type}
                </span>
              </div>
              <p style={{ color: '#666', fontSize: '14px', marginBottom: '10px' }}>
                {provider.description}
              </p>
              <div style={{ marginBottom: '10px' }}>
                <strong style={{ fontSize: '12px' }}>Models: </strong>
                <span style={{ fontSize: '14px' }}>{provider.model_count || 0}</span>
              </div>
              <div style={{ marginBottom: '15px' }}>
                <strong style={{ fontSize: '12px' }}>Required Credentials:</strong>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                  {provider.credentials.map((cred, idx) => (
                    <li key={idx} style={{ fontSize: '12px' }}>
                      {cred.label} ({cred.type})
                    </li>
                  ))}
                </ul>
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => openEditModal(provider)}
                  style={{
                    flex: 1,
                    padding: '5px',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(provider.id)}
                  style={{
                    flex: 1,
                    padding: '5px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                  disabled={!!provider.model_count && provider.model_count > 0}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Provider Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h3>{editingProvider ? 'Edit Provider' : 'Add New Provider'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
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

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Provider Type:</label>
                <input
                  type="text"
                  value={formData.provider_type}
                  onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
                  required
                  disabled={!!editingProvider}
                  placeholder="e.g., openai, anthropic, custom"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: editingProvider ? '#e9ecef' : 'white'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Icon Path:</label>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  rows={3}
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
                  Credential Fields:
                  <button
                    type="button"
                    onClick={addCredentialField}
                    style={{
                      marginLeft: '10px',
                      padding: '2px 8px',
                      fontSize: '12px',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    + Add Field
                  </button>
                </label>
                {formData.credentials.map((cred, index) => (
                  <div key={index} style={{
                    padding: '10px',
                    marginBottom: '10px',
                    border: '1px solid #e9ecef',
                    borderRadius: '4px'
                  }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <input
                        type="text"
                        placeholder="Field name"
                        value={cred.field}
                        onChange={(e) => updateCredentialField(index, { field: e.target.value })}
                        style={{ padding: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
                      />
                      <input
                        type="text"
                        placeholder="Label"
                        value={cred.label}
                        onChange={(e) => updateCredentialField(index, { label: e.target.value })}
                        style={{ padding: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
                      />
                      <select
                        value={cred.type}
                        onChange={(e) => updateCredentialField(index, { type: e.target.value as any })}
                        style={{ padding: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
                      >
                        <option value="text">Text</option>
                        <option value="password">Password</option>
                        <option value="select">Select</option>
                        <option value="number">Number</option>
                      </select>
                      <input
                        type="text"
                        placeholder="Description"
                        value={cred.description}
                        onChange={(e) => updateCredentialField(index, { description: e.target.value })}
                        style={{ padding: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
                      />
                    </div>
                    <div style={{ marginTop: '5px', display: 'flex', justifyContent: 'space-between' }}>
                      <label>
                        <input
                          type="checkbox"
                          checked={cred.required}
                          onChange={(e) => updateCredentialField(index, { required: e.target.checked })}
                        />
                        Required
                      </label>
                      <button
                        type="button"
                        onClick={() => removeCredentialField(index)}
                        style={{
                          padding: '2px 8px',
                          fontSize: '12px',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false)
                    setEditingProvider(null)
                    resetForm()
                  }}
                  style={{
                    padding: '10px 20px',
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
                    padding: '10px 20px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {editingProvider ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}