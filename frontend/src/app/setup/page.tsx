'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { useApiKey, useNotifications, useLoading } from '@/lib/stores/app-store'
import { apiClient } from '@/lib/api/client'

export default function SetupPage() {
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [connectionTest, setConnectionTest] = useState<{
    connected: boolean
    authenticated: boolean
    message: string
  } | null>(null)

  const { apiKey, apiKeyInfo, setApiKey, setApiKeyInfo, clearApiKey } = useApiKey()
  const { addNotification } = useNotifications()
  const { loading, setLoading, clearLoading } = useLoading()

  // Test connection on mount and when API key changes
  useEffect(() => {
    const testConnection = async () => {
      setLoading({ isLoading: true, message: 'Testing connection...' })
      try {
        const result = await apiClient.testConnection()
        setConnectionTest(result)
        
        if (result.authenticated) {
          // Get API key info
          const keyInfo = await apiClient.getApiKeyInfo()
          setApiKeyInfo(keyInfo)
          addNotification({
            type: 'success',
            title: 'Connection Successful',
            message: 'Your API key is working correctly!',
          })
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error'
        addNotification({
          type: 'error',
          title: 'Connection Failed',
          message: `Failed to connect to the API: ${errorMessage}`,
        })
        setConnectionTest({
          connected: false,
          authenticated: false,
          message: errorMessage,
        })
      } finally {
        clearLoading()
      }
    }

    if (apiKey) {
      testConnection()
    }
  }, [apiKey, setLoading, clearLoading, setApiKeyInfo, addNotification])

  const handleTestConnection = async () => {
    setLoading({ isLoading: true, message: 'Testing connection...' })
    try {
      const result = await apiClient.testConnection()
      setConnectionTest(result)
      
      if (result.authenticated) {
        // Get API key info
        const keyInfo = await apiClient.getApiKeyInfo()
        setApiKeyInfo(keyInfo)
        addNotification({
          type: 'success',
          title: 'Connection Successful',
          message: 'Your API key is working correctly!',
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      addNotification({
        type: 'error',
        title: 'Connection Failed',
        message: errorMessage,
      })
    } finally {
      clearLoading()
    }
  }

  const handleSaveApiKey = () => {
    if (!apiKeyInput.trim()) {
      addNotification({
        type: 'warning',
        title: 'Invalid Input',
        message: 'Please enter a valid API key.',
      })
      return
    }

    setApiKey(apiKeyInput.trim())
    apiClient.setApiKey(apiKeyInput.trim())
    setApiKeyInput('')
    
    addNotification({
      type: 'info',
      title: 'API Key Saved',
      message: 'Testing connection...',
    })
  }

  const handleGenerateApiKey = async () => {
    setIsGenerating(true)
    try {
      // For now, show instructions since we need to connect to the backend
      addNotification({
        type: 'info',
        title: 'Generate API Key',
        message: 'Please use the backend API to generate a new API key, then paste it here.',
        duration: 8000,
      })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: errorMessage,
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleClearApiKey = () => {
    clearApiKey()
    apiClient.clearApiKey()
    setConnectionTest(null)
    addNotification({
      type: 'info',
      title: 'API Key Cleared',
      message: 'You will need to set up a new API key to use the travel planner.',
    })
  }

  return (
    <div className="container mx-auto px-4 py-12 max-w-2xl">
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">API Setup</h1>
          <p className="text-lg text-gray-600">
            Configure your API key to start using WanderWise travel planner
          </p>
        </div>

        {/* Current Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Connection Status</h2>
          
          {loading.isLoading ? (
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner size="md" message={loading.message} />
            </div>
          ) : connectionTest ? (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <div className={`h-3 w-3 rounded-full ${connectionTest.connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="font-medium">
                  {connectionTest.connected ? 'Connected to API' : 'Not Connected'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className={`h-3 w-3 rounded-full ${connectionTest.authenticated ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="font-medium">
                  {connectionTest.authenticated ? 'Authenticated' : 'Not Authenticated'}
                </span>
              </div>
              
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                {connectionTest.message}
              </p>

              {apiKeyInfo && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <h3 className="font-medium text-green-900">API Key Information</h3>
                  <div className="mt-2 space-y-1 text-sm text-green-700">
                    <p><strong>Name:</strong> {apiKeyInfo.name}</p>
                    <p><strong>Rate Limit:</strong> {apiKeyInfo.rate_limit} requests/minute</p>
                    <p><strong>Created:</strong> {new Date(apiKeyInfo.created_at).toLocaleDateString()}</p>
                    {apiKeyInfo.last_used && (
                      <p><strong>Last Used:</strong> {new Date(apiKeyInfo.last_used).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-500">No API key configured</p>
          )}
        </div>

        {/* API Key Input */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">API Key Configuration</h2>
          
          {!apiKey ? (
            <div className="space-y-4">
              <Input
                label="API Key"
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Enter your WanderWise API key"
                helperText="Paste your API key here to connect to the WanderWise backend"
              />
              
              <div className="flex gap-3">
                <Button onClick={handleSaveApiKey} className="flex-1">
                  Save API Key
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleGenerateApiKey}
                  loading={isGenerating}
                  disabled={isGenerating}
                >
                  Generate New Key
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-800 font-medium">API Key Active</span>
                </div>
                <span className="text-green-600 text-sm">
                  ••••••••{apiKey.slice(-4)}
                </span>
              </div>
              
              <div className="flex gap-3">
                <Button variant="outline" onClick={handleTestConnection}>
                  Test Connection
                </Button>
                <Button variant="destructive" onClick={handleClearApiKey}>
                  Clear API Key
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">How to Get Your API Key</h2>
          <div className="space-y-3 text-blue-800">
            <p className="text-sm">
              1. Start your WanderWise backend server (if not already running):
            </p>
            <div className="bg-blue-100 p-3 rounded font-mono text-sm">
              cd /path/to/travel_planner<br />
              python start_api.py
            </div>
            
            <p className="text-sm">
              2. Generate a new API key using the backend API:
            </p>
            <div className="bg-blue-100 p-3 rounded font-mono text-sm">
              curl -X POST http://localhost:8000/auth/generate-key \<br />
              &nbsp;&nbsp;-H &ldquo;Content-Type: application/json&rdquo; \<br />
              &nbsp;&nbsp;-d &apos;{'{'}name: &ldquo;my-frontend-key&rdquo;{'}'}{"'"}&apos;
            </div>
            
            <p className="text-sm">
              3. Copy the generated API key and paste it above.
            </p>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center space-x-4">
          {apiKey && connectionTest?.authenticated ? (
            <Link href="/">
              <Button size="lg">
                🎉 Start Planning Your Trip
              </Button>
            </Link>
          ) : (
            <Link href="/">
              <Button variant="outline">
                Back to Home
              </Button>
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
