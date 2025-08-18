'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Key, CheckCircle, XCircle, RefreshCw, Eye, EyeOff } from 'lucide-react'

interface APIKeyManagerProps {
  onKeyValid?: (isValid: boolean) => void
}

export function APIKeyManager({ onKeyValid }: APIKeyManagerProps) {
  const [apiKey, setApiKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<{
    connected: boolean
    authenticated: boolean
    message: string
  } | null>(null)

  useEffect(() => {
    // Check if there's a saved API key and validate it
    const savedKey = localStorage.getItem('wanderwise_api_key')
    if (savedKey) {
      setApiKey(savedKey)
      validateConnection(savedKey)
    }
  }, [])

  const validateConnection = async (key?: string) => {
    setIsValidating(true)
    
    try {
      if (key) {
        apiClient.setApiKey(key)
      }
      
      const status = await apiClient.testConnection()
      setConnectionStatus(status)
      onKeyValid?.(status.authenticated)
      
    } catch (error) {
      setConnectionStatus({
        connected: false,
        authenticated: false,
        message: 'Failed to test connection'
      })
      onKeyValid?.(false)
    } finally {
      setIsValidating(false)
    }
  }

  const handleSaveKey = () => {
    if (apiKey.trim()) {
      apiClient.setApiKey(apiKey.trim())
      validateConnection()
    }
  }

  const handleGenerateKey = async () => {
    try {
      setIsValidating(true)
      
      // Call the backend to generate a new key
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/generate-key`)
      const data = await response.json()
      
      if (data.api_key) {
        setApiKey(data.api_key)
        apiClient.setApiKey(data.api_key)
        await validateConnection()
        alert(`New API key generated! Make sure to add it to your backend's API_KEYS environment variable: ${data.api_key}`)
      }
    } catch (error) {
      console.error('Failed to generate API key:', error)
      alert('Failed to generate API key. Make sure the backend server is running.')
    } finally {
      setIsValidating(false)
    }
  }

  const handleClearKey = () => {
    setApiKey('')
    apiClient.clearApiKey()
    setConnectionStatus(null)
    onKeyValid?.(false)
  }

  const getStatusBadge = () => {
    if (!connectionStatus) return null

    if (!connectionStatus.connected) {
      return <Badge variant="destructive" className="flex items-center gap-1">
        <XCircle className="w-3 h-3" />
        Disconnected
      </Badge>
    }

    if (!connectionStatus.authenticated) {
      return <Badge variant="secondary" className="flex items-center gap-1">
        <XCircle className="w-3 h-3" />
        Not Authenticated
      </Badge>
    }

    return <Badge variant="default" className="flex items-center gap-1 bg-green-100 text-green-800">
      <CheckCircle className="w-3 h-3" />
      Connected
    </Badge>
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Key className="w-5 h-5" />
          API Configuration
        </CardTitle>
        <CardDescription>
          Configure your API key to connect to the WanderWise backend service
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Connection Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status:</span>
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => validateConnection()}
              disabled={isValidating}
            >
              <RefreshCw className={`w-4 h-4 ${isValidating ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {connectionStatus?.message && (
          <div className={`text-sm p-3 rounded-md ${
            connectionStatus.authenticated 
              ? 'bg-green-50 text-green-700 border border-green-200' 
              : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
          }`}>
            {connectionStatus.message}
          </div>
        )}

        {/* API Key Input */}
        <div className="space-y-2">
          <label className="text-sm font-medium">API Key</label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                type={showKey ? 'text' : 'password'}
                placeholder="Enter your API key..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowKey(!showKey)}
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
            </div>
            <Button 
              onClick={handleSaveKey}
              disabled={!apiKey.trim() || isValidating}
            >
              Save
            </Button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={handleGenerateKey}
            disabled={isValidating}
          >
            Generate New Key
          </Button>
          
          {apiKey && (
            <Button 
              variant="outline" 
              onClick={handleClearKey}
            >
              Clear Key
            </Button>
          )}
        </div>

        {/* Help Text */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>• Make sure the WanderWise backend is running on http://localhost:8000</p>
          <p>• You can generate a new API key using the &ldquo;Generate New Key&rdquo; button</p>
          <p>• Remember to add generated keys to your backend&apos;s API_KEYS environment variable</p>
        </div>
      </CardContent>
    </Card>
  )
}
