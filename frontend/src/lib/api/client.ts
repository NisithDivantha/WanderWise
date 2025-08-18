import axios, { AxiosInstance, AxiosError } from 'axios'
import { 
  TravelPlanRequest, 
  TravelPlan, 
  APIResponse, 
  APIKeyInfo,
  APIKeyGenerationRequest,
  APIKeyGenerationResponse
} from '@/types/api'

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000')
const TRAVEL_PLAN_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_TRAVEL_PLAN_TIMEOUT || '300000') // 5 minutes for travel plan generation

class APIClient {
  private client: AxiosInstance
  private apiKey: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add API key if available
        if (this.apiKey) {
          config.headers['X-API-Key'] = this.apiKey
        }

        // Add timestamp for debugging
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        }
        return response
      },
      (error: AxiosError) => {
        // Always log errors for debugging
        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data)
        console.error('Full error details:', {
          message: error.message,
          code: error.code,
          response: error.response?.data,
          status: error.response?.status,
          headers: error.response?.headers
        })
        
        // Handle common errors
        if (error.response?.status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.')
        }
        
        if (error.response?.status === 401) {
          throw new Error('Invalid API key. Please check your authentication.')
        }
        
        if (error.response?.status === 500) {
          throw new Error('Server error. Please try again later.')
        }

        // Network error
        if (!error.response) {
          throw new Error('Network error. Please check your connection.')
        }

        throw error
      }
    )

    // Load API key from localStorage on initialization
    this.loadApiKey()
  }

  /**
   * Set API key for authentication
   */
  setApiKey(key: string) {
    this.apiKey = key
    // Save to localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('wanderwise_api_key', key)
    }
  }

  /**
   * Load API key from localStorage
   */
  private loadApiKey() {
    if (typeof window !== 'undefined') {
      const savedKey = localStorage.getItem('wanderwise_api_key')
      if (savedKey) {
        this.apiKey = savedKey
      }
    }
  }

  /**
   * Clear API key
   */
  clearApiKey() {
    this.apiKey = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('wanderwise_api_key')
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get('/health')
    return response.data
  }

  /**
   * Generate travel plan
   */
  async generateTravelPlan(request: TravelPlanRequest): Promise<TravelPlan> {
    const response = await this.client.post('/generate-travel-plan', request, {
      timeout: TRAVEL_PLAN_TIMEOUT // Use extended timeout for travel plan generation
    })
    
    // Debug: Log the response structure
    console.log('🎯 API Response received:', response.status, response.statusText)
    console.log('📦 Response data structure:', Object.keys(response.data))
    console.log('📝 Full response data:', response.data)
    
    // Your backend returns the plan directly, not wrapped in APIResponse
    return response.data
  }

  /**
   * Generate travel plan without authentication (public endpoint)
   */
  async generateTravelPlanPublic(request: TravelPlanRequest): Promise<TravelPlan> {
    const response = await this.client.post('/public/generate-travel-plan', request, {
      timeout: TRAVEL_PLAN_TIMEOUT // Use extended timeout for travel plan generation
    })
    
    // Debug: Log the response structure
    console.log('🎯 API Response received:', response.status, response.statusText)
    console.log('📦 Response data structure:', Object.keys(response.data))
    console.log('📝 Full response data:', response.data)
    
    // Your backend returns the plan directly, not wrapped in APIResponse
    return response.data
  }

  /**
   * Get available destinations
   */
  async getDestinations(): Promise<string[]> {
    const response = await this.client.get('/destinations')
    
    // Your backend returns { destinations: [...] }
    return response.data.destinations || []
  }

  /**
   * Download travel plan file
   */
  async downloadPlan(planId: string, fileType: 'json' | 'txt' = 'json'): Promise<Blob> {
    const response = await this.client.get(`/download/${fileType}`, {
      params: { plan_id: planId },
      responseType: 'blob',
    })
    
    return response.data
  }

  /**
   * Get API key information
   */
  async getApiKeyInfo(): Promise<APIKeyInfo> {
    const response = await this.client.get<APIResponse<APIKeyInfo>>('/auth/info')
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch API key info')
    }
    
    return response.data.data
  }

  /**
   * Generate new API key
   */
  async generateApiKey(request: APIKeyGenerationRequest): Promise<APIKeyGenerationResponse> {
    const response = await this.client.post<APIResponse<APIKeyGenerationResponse>>('/auth/generate-key', request)
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to generate API key')
    }
    
    return response.data.data
  }

  /**
   * Test API connection and authentication
   */
  async testConnection(): Promise<{ connected: boolean; authenticated: boolean; message: string }> {
    try {
      // Test basic connection
      await this.healthCheck()
      
      if (!this.apiKey) {
        return {
          connected: true,
          authenticated: false,
          message: 'Connected but no API key provided'
        }
      }

      // Test authentication
      await this.getApiKeyInfo()
      
      return {
        connected: true,
        authenticated: true,
        message: 'Connected and authenticated successfully'
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      
      if (errorMessage.includes('Network error')) {
        return {
          connected: false,
          authenticated: false,
          message: 'Cannot connect to API server'
        }
      }
      
      if (errorMessage.includes('Invalid API key')) {
        return {
          connected: true,
          authenticated: false,
          message: 'Invalid API key'
        }
      }
      
      return {
        connected: true,
        authenticated: false,
        message: errorMessage
      }
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient()

// Export the class for testing or custom instances
export { APIClient }
