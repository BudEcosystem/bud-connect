import axios, { AxiosError } from 'axios'
import { ErrorResponse } from '@/types'

// Create axios instance for backend API calls
// Development: Vite proxy intercepts backend routes and forwards to Kubernetes backend
// Production: Traefik routes backend paths directly to backend service
const apiClient = axios.create({
  baseURL: '', // Empty string for same-origin requests
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Log requests in debug mode
    if (import.meta.env.VITE_DEBUG_MODE === 'true') {
      console.log('API Request:', config.method?.toUpperCase(), config.url, 'Base URL:', config.baseURL)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in debug mode
    if (import.meta.env.VITE_DEBUG_MODE === 'true') {
      console.log('API Response:', response.status, response.config.url)
    }
    return response
  },
  async (error: AxiosError<ErrorResponse>) => {
    // Log errors in debug mode
    if (import.meta.env.VITE_DEBUG_MODE === 'true') {
      console.error('API Error:', error.response?.status, error.config?.url, error.response?.data)
    }
    
    // Handle 401 Unauthorized - try to refresh token
    if (error.response?.status === 401 && error.config) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken && !error.config.url?.includes('/auth/')) {
        try {
          // Use apiClient to ensure proper baseURL and proxy routing in development
          const response = await apiClient.post('/auth/refresh', {
            refresh_token: refreshToken
          })
          
          // Store new tokens
          localStorage.setItem('access_token', response.data.access_token)
          localStorage.setItem('refresh_token', response.data.refresh_token)
          
          // Retry original request with new token
          error.config.headers.Authorization = `Bearer ${response.data.access_token}`
          return apiClient.request(error.config)
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/admin/login'
        }
      } else {
        // No refresh token or auth endpoint failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/admin/login'
      }
    }
    
    // FastAPI sends error messages in the 'detail' field
    if (error.response?.data) {
      const errorData = error.response.data as any
      const errorMessage = errorData.detail || errorData.message || 'An error occurred'
      throw new Error(errorMessage)
    }
    throw error
  }
)

// Export the configured axios instance directly
export { apiClient }