import { useState, useEffect } from 'react'
import { licenseApi } from '../api'
import { License, LicenseCreate, LicenseUpdate, FAQ } from '../types'

const SUITABILITY_OPTIONS = ['MOST', 'GOOD', 'LOW', 'WORST']
const LICENSE_TYPES = [
  'Permissive Open Source',
  'Copyleft Open Source',
  'Proprietary',
  'Commercial',
  'Research Only',
  'Custom'
]

const SUITABILITY_COLORS: Record<string, string> = {
  MOST: '#28a745',
  GOOD: '#17a2b8',
  LOW: '#ffc107',
  WORST: '#dc3545'
}

export function SimpleLicenses() {
  const [licenses, setLicenses] = useState<License[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showExtractModal, setShowExtractModal] = useState(false)
  const [editingLicense, setEditingLicense] = useState<License | null>(null)
  const [expandedLicenses, setExpandedLicenses] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<string>('')
  const [filterSuitability, setFilterSuitability] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [extractSource, setExtractSource] = useState<'url' | 'text'>('url')
  const [extractContent, setExtractContent] = useState('')
  
  const [formData, setFormData] = useState<LicenseCreate>({
    key: '',
    name: '',
    type: 'Permissive Open Source',
    type_description: '',
    type_suitability: 'GOOD',
    faqs: []
  })

  useEffect(() => {
    fetchLicenses()
  }, [currentPage, searchTerm, filterType, filterSuitability])

  const fetchLicenses = async () => {
    try {
      setLoading(true)
      const params: any = { 
        page: currentPage, 
        page_size: 10
      }
      
      if (searchTerm) params.search = searchTerm
      if (filterType) params.license_type = filterType
      if (filterSuitability) params.suitability = filterSuitability
      
      const response = await licenseApi.getAll(params)
      setLicenses(response.licenses)
      setTotalPages(Math.ceil(response.total / 10))
    } catch (error) {
      console.error('Failed to fetch licenses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingLicense) {
        const updateData: LicenseUpdate = {
          key: formData.key,
          name: formData.name,
          type: formData.type,
          type_description: formData.type_description,
          type_suitability: formData.type_suitability,
          faqs: formData.faqs
        }
        await licenseApi.update(editingLicense.id, updateData)
      } else {
        await licenseApi.create(formData)
      }
      setShowAddModal(false)
      setEditingLicense(null)
      resetForm()
      fetchLicenses()
    } catch (error) {
      console.error('Failed to save license:', error)
      alert('Failed to save license. Check if the key is unique.')
    }
  }

  const handleExtract = async () => {
    try {
      const request: any = {
        source_type: extractSource,
        source: extractContent
      }
      
      const extracted = await licenseApi.extract(request)
      
      // Pre-fill the form with extracted data
      setFormData({
        key: extracted.key || '',
        name: extracted.name || '',
        type: extracted.type || 'Custom',
        type_description: extracted.type_description || '',
        type_suitability: extracted.type_suitability || 'LOW',
        faqs: extracted.faqs || []
      })
      
      setShowExtractModal(false)
      setShowAddModal(true)
      setExtractContent('')
    } catch (error) {
      console.error('Failed to extract license:', error)
      alert('Failed to extract license information')
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this license?')) {
      try {
        await licenseApi.delete(id)
        fetchLicenses()
      } catch (error) {
        console.error('Failed to delete license:', error)
        alert('Failed to delete license. It may be in use by models.')
      }
    }
  }

  const handleEdit = (license: License) => {
    setEditingLicense(license)
    setFormData({
      key: license.key,
      name: license.name,
      type: license.type,
      type_description: license.type_description,
      type_suitability: license.type_suitability,
      faqs: license.faqs || []
    })
    setShowAddModal(true)
  }

  const toggleExpand = (licenseId: string) => {
    const newExpanded = new Set(expandedLicenses)
    if (newExpanded.has(licenseId)) {
      newExpanded.delete(licenseId)
    } else {
      newExpanded.add(licenseId)
    }
    setExpandedLicenses(newExpanded)
  }

  const resetForm = () => {
    setFormData({
      key: '',
      name: '',
      type: 'Permissive Open Source',
      type_description: '',
      type_suitability: 'GOOD',
      faqs: []
    })
  }

  const addFAQ = () => {
    setFormData({
      ...formData,
      faqs: [
        ...formData.faqs,
        {
          question: '',
          answer: '',
          reason: [],
          impact: 'NEUTRAL'
        }
      ]
    })
  }

  const updateFAQ = (index: number, field: keyof FAQ, value: any) => {
    const newFAQs = [...formData.faqs]
    if (field === 'reason' && typeof value === 'string') {
      // Convert comma-separated string to array
      newFAQs[index] = { ...newFAQs[index], [field]: value.split(',').map(s => s.trim()).filter(s => s) }
    } else {
      newFAQs[index] = { ...newFAQs[index], [field]: value }
    }
    setFormData({ ...formData, faqs: newFAQs })
  }

  const removeFAQ = (index: number) => {
    setFormData({
      ...formData,
      faqs: formData.faqs.filter((_, i) => i !== index)
    })
  }

  if (loading && licenses.length === 0) {
    return <div>Loading licenses...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>License Management</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => {
              setShowExtractModal(true)
            }}
            style={{
              padding: '10px 20px',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Extract License
          </button>
          <button
            onClick={() => {
              setEditingLicense(null)
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
            Add License
          </button>
        </div>
      </div>

      {/* Filters */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search licenses..."
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
          value={filterType}
          onChange={(e) => {
            setFilterType(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Types</option>
          {LICENSE_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <select
          value={filterSuitability}
          onChange={(e) => {
            setFilterSuitability(e.target.value)
            setCurrentPage(1)
          }}
          style={{
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Suitability</option>
          {SUITABILITY_OPTIONS.map(suit => (
            <option key={suit} value={suit}>{suit}</option>
          ))}
        </select>
      </div>

      {/* License List */}
      <div style={{ backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        {licenses.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>No licenses found</div>
        ) : (
          licenses.map((license) => (
            <div key={license.id} style={{ borderBottom: '1px solid #eee' }}>
              <div style={{ 
                padding: '15px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                backgroundColor: expandedLicenses.has(license.id) ? '#f8f9fa' : 'white'
              }}
              onClick={() => toggleExpand(license.id)}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                    <h3 style={{ margin: 0 }}>{license.name}</h3>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: SUITABILITY_COLORS[license.type_suitability] || '#6c757d',
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}>
                      {license.type_suitability}
                    </span>
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    <strong>Key:</strong> {license.key} | <strong>Type:</strong> {license.type}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEdit(license)
                    }}
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
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(license.id)
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
              
              {expandedLicenses.has(license.id) && (
                <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderTop: '1px solid #e9ecef' }}>
                  <p><strong>Description:</strong> {license.type_description}</p>
                  {license.faqs && license.faqs.length > 0 && (
                    <div>
                      <h4>FAQs:</h4>
                      {license.faqs.map((faq, idx) => (
                        <div key={idx} style={{ 
                          marginBottom: '15px',
                          padding: '10px',
                          backgroundColor: 'white',
                          borderRadius: '4px'
                        }}>
                          <p><strong>Q:</strong> {faq.question}</p>
                          <p><strong>A:</strong> {faq.answer}</p>
                          {faq.reason && faq.reason.length > 0 && (
                            <p style={{ fontSize: '12px', color: '#666' }}>
                              <strong>Reason:</strong> {faq.reason.join(', ')}
                            </p>
                          )}
                          {faq.impact && (
                            <span style={{
                              padding: '2px 6px',
                              borderRadius: '3px',
                              fontSize: '11px',
                              backgroundColor: faq.impact === 'POSITIVE' ? '#d4edda' : 
                                             faq.impact === 'NEGATIVE' ? '#f8d7da' : '#f0f0f0',
                              color: faq.impact === 'POSITIVE' ? '#155724' : 
                                     faq.impact === 'NEGATIVE' ? '#721c24' : '#666'
                            }}>
                              Impact: {faq.impact}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
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

      {/* Add/Edit Modal */}
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
            width: '700px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h2>{editingLicense ? 'Edit License' : 'Add New License'}</h2>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Key * (unique identifier, e.g., "mit", "apache-2.0")
                </label>
                <input
                  type="text"
                  value={formData.key}
                  onChange={(e) => setFormData({ ...formData, key: e.target.value })}
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

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Type *
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                >
                  {LICENSE_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>
                  Type Description *
                </label>
                <textarea
                  value={formData.type_description}
                  onChange={(e) => setFormData({ ...formData, type_description: e.target.value })}
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
                  Suitability *
                </label>
                <select
                  value={formData.type_suitability}
                  onChange={(e) => setFormData({ ...formData, type_suitability: e.target.value as 'MOST' | 'GOOD' | 'LOW' | 'WORST' })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                >
                  {SUITABILITY_OPTIONS.map(suit => (
                    <option key={suit} value={suit}>{suit}</option>
                  ))}
                </select>
              </div>

              {/* FAQs Section */}
              <div style={{ marginBottom: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ fontWeight: 'bold' }}>FAQs</label>
                  <button
                    type="button"
                    onClick={addFAQ}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Add FAQ
                  </button>
                </div>
                
                {formData.faqs.map((faq, index) => (
                  <div key={index} style={{
                    padding: '10px',
                    marginBottom: '10px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    border: '1px solid #dee2e6'
                  }}>
                    <div style={{ marginBottom: '10px' }}>
                      <input
                        type="text"
                        placeholder="Question"
                        value={faq.question}
                        onChange={(e) => updateFAQ(index, 'question', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '5px',
                          border: '1px solid #ddd',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <input
                        type="text"
                        placeholder="Answer"
                        value={faq.answer}
                        onChange={(e) => updateFAQ(index, 'answer', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '5px',
                          border: '1px solid #ddd',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <input
                        type="text"
                        placeholder="Reasons (comma-separated)"
                        value={faq.reason?.join(', ') || ''}
                        onChange={(e) => updateFAQ(index, 'reason', e.target.value)}
                        style={{
                          width: '100%',
                          padding: '5px',
                          border: '1px solid #ddd',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <select
                        value={faq.impact || 'NEUTRAL'}
                        onChange={(e) => updateFAQ(index, 'impact', e.target.value)}
                        style={{
                          padding: '5px',
                          border: '1px solid #ddd',
                          borderRadius: '3px'
                        }}
                      >
                        <option value="POSITIVE">POSITIVE</option>
                        <option value="NEGATIVE">NEGATIVE</option>
                        <option value="NEUTRAL">NEUTRAL</option>
                      </select>
                      <button
                        type="button"
                        onClick={() => removeFAQ(index)}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '3px',
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
                    setEditingLicense(null)
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
                  {editingLicense ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Extract License Modal */}
      {showExtractModal && (
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
            width: '600px'
          }}>
            <h2>Extract License Information</h2>
            
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Source Type
              </label>
              <select
                value={extractSource}
                onChange={(e) => setExtractSource(e.target.value as 'url' | 'text')}
                style={{
                  width: '100%',
                  padding: '8px',
                  border: '1px solid #ddd',
                  borderRadius: '4px'
                }}
              >
                <option value="url">URL</option>
                <option value="text">Text</option>
              </select>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                {extractSource === 'url' ? 'License URL' : 'License Text'}
              </label>
              {extractSource === 'url' ? (
                <input
                  type="text"
                  value={extractContent}
                  onChange={(e) => setExtractContent(e.target.value)}
                  placeholder="https://example.com/license"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              ) : (
                <textarea
                  value={extractContent}
                  onChange={(e) => setExtractContent(e.target.value)}
                  placeholder="Paste license text here..."
                  rows={10}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              )}
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowExtractModal(false)
                  setExtractContent('')
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
                onClick={handleExtract}
                disabled={!extractContent}
                style={{
                  padding: '8px 16px',
                  backgroundColor: extractContent ? '#17a2b8' : '#ccc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: extractContent ? 'pointer' : 'not-allowed'
                }}
              >
                Extract & Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}