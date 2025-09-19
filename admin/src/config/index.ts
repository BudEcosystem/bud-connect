// Application configuration from environment variables

interface AppConfig {
  api: {
    baseUrl: string
    timeout: number
    // If true, uses proxy /api path; if false, uses direct URL
    useProxy: boolean
  }
  features: {
    enableMockData: boolean
    debugMode: boolean
  }
}

// Helper function to get environment variable with fallback
const getEnvVar = (key: string, defaultValue: string = ''): string => {
  return import.meta.env[key] || defaultValue
}

// Helper function to parse boolean environment variables
const getEnvBool = (key: string, defaultValue: boolean = false): boolean => {
  const value = getEnvVar(key, String(defaultValue))
  return value === 'true' || value === '1'
}

// Helper function to parse number environment variables
const getEnvNumber = (key: string, defaultValue: number): number => {
  const value = getEnvVar(key, String(defaultValue))
  const parsed = parseInt(value, 10)
  return isNaN(parsed) ? defaultValue : parsed
}

// Determine if we should use the proxy or direct URL
const shouldUseProxy = (): boolean => {
  const baseUrl = getEnvVar('VITE_API_BASE_URL', '')
  
  // In production, always use proxy to ensure HTTPS
  if (import.meta.env.MODE === 'production') {
    return true
  }
  
  // In development mode, check if we should use proxy
  if (import.meta.env.MODE === 'development') {
    // If baseUrl starts with /admin/api or /api, use proxy
    if (baseUrl.startsWith('/admin/api') || baseUrl.startsWith('/api')) {
      return true
    }
    // Otherwise use direct URL for development
    return false
  }
  
  // Default to proxy
  return true
}

export const config: AppConfig = {
  api: {
    baseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:9088'),
    timeout: getEnvNumber('VITE_API_TIMEOUT', 30000),
    useProxy: shouldUseProxy()
  },
  features: {
    enableMockData: getEnvBool('VITE_ENABLE_MOCK_DATA', false),
    debugMode: getEnvBool('VITE_DEBUG_MODE', false)
  }
}

// Log configuration in debug mode
if (config.features.debugMode) {
  console.log('App Configuration:', config)
}

export default config