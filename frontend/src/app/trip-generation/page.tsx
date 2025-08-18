'use client'

import { useState, useEffect } from 'react'
import { TravelFormData } from '@/lib/schemas/travel-form'
import { TravelPlanningForm } from '@/components/forms/travel-planning-form'
import { GenerationProgress } from '@/components/ui/generation-progress'
import { TravelPlanResults } from '@/components/ui/travel-plan-results'
import { NotificationContainer } from '@/components/ui/notification-container'
import { APIKeyManager } from '@/components/api/api-key-manager'
import { useTravelPlanStore } from '@/lib/stores/travel-plan-store'
import { usePlanManagementStore } from '../../lib/stores/plan-management-store'
import { tripGenerationService } from '@/lib/services/trip-generation'
import { TravelPlanRequest, TravelPlan } from '@/types/api'
import { Button } from '@/components/ui/button'
import { ArrowLeft, RefreshCw, Settings } from 'lucide-react'
import { useNotificationStore } from '../../lib/stores/notification-store'

export default function TripGenerationPage() {
  const [currentView, setCurrentView] = useState<'form' | 'generating' | 'results' | 'api-setup'>('form')
  const [isApiKeyValid, setIsApiKeyValid] = useState(false)
  const [showApiSetup, setShowApiSetup] = useState(false)
  
  const { 
    isGenerating, 
    currentPlan, 
    error, 
    resetGeneration 
  } = useTravelPlanStore()
  
  const { savePlan } = usePlanManagementStore()
  const { addNotification } = useNotificationStore()

  useEffect(() => {
    // Check if API key is already configured and set it in the client
    const savedKey = localStorage.getItem('wanderwise_api_key')
    if (savedKey) {
      // API key exists, no need to change view since we start with 'form'
      setIsApiKeyValid(true)
    }
  }, [])

  const handleApiKeyValidation = (isValid: boolean) => {
    setIsApiKeyValid(isValid)
    if (isValid && currentView === 'api-setup') {
      setCurrentView('form')
      addNotification({
        type: 'success',
        title: 'Connected!',
        message: 'Successfully connected to WanderWise API. You can now generate travel plans.',
        duration: 3000
      })
    }
  }

  const handleFormSubmit = async (data: TravelFormData) => {
    try {
      setCurrentView('generating')
      
      const request: TravelPlanRequest = {
        destination: data.destination,
        start_date: data.startDate,
        end_date: data.endDate,
        interests: data.interests,
        budget: data.budget as 'low' | 'medium' | 'high',
        group_size: 1
      }

      const result = await tripGenerationService.generateTravelPlan(request)
      
      // Auto-save the generated plan
      const savedPlanId = savePlan(result, `${result.destination} Adventure`)

      addNotification({
        type: 'success',
        title: 'Trip Generated!',
        message: 'Your personalized travel plan has been created and saved.',
        duration: 5000
      })

      setCurrentView('results')
    } catch (error) {
      console.error('Trip generation error:', error)
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: error instanceof Error ? error.message : 'Failed to generate travel plan',
        duration: 5000
      })
      setCurrentView('form')
    }
  }

  const handleSavePlan = (plan: TravelPlan) => {
    savePlan(plan, `${plan.destination} Trip`)

    addNotification({
      type: 'success',
      title: 'Plan Saved!',
      message: 'Your travel plan has been saved to your collection.',
      duration: 3000
    })
  }

  const handleSharePlan = (plan: TravelPlan) => {
    // Create a shareable URL or copy to clipboard
    const shareData = {
      title: `Travel Plan: ${plan.destination}`,
      text: `Check out this amazing travel plan for ${plan.destination}!`,
      url: window.location.href
    }

    if (navigator.share) {
      navigator.share(shareData)
    } else {
      navigator.clipboard.writeText(window.location.href)
      addNotification({
        type: 'success',
        title: 'Link Copied!',
        message: 'The trip link has been copied to your clipboard.',
        duration: 3000
      })
    }
  }

  const handleDownloadPlan = (plan: TravelPlan, format: 'json' | 'txt') => {
    const content = format === 'json' 
      ? JSON.stringify(plan, null, 2)
      : formatPlanAsText(plan)
    
    const blob = new Blob([content], { type: format === 'json' ? 'application/json' : 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `travel-plan-${plan.destination.replace(/\s+/g, '-').toLowerCase()}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    addNotification({
      type: 'success',
      title: 'Download Started!',
      message: `Your travel plan has been downloaded as ${format.toUpperCase()}.`,
      duration: 3000
    })
  }

  const formatPlanAsText = (plan: TravelPlan): string => {
    let text = `Travel Plan: ${plan.destination}\n`
    text += `Duration: ${plan.start_date} to ${plan.end_date}\n\n`
    text += `Summary:\n${plan.executive_summary}\n\n`
    
    if (plan.itinerary.length > 0) {
      text += 'Itinerary:\n'
      plan.itinerary.forEach((day, index) => {
        text += `\nDay ${index + 1} (${day.date}):\n`
        day.activities.forEach(activity => {
          text += `  ${activity.time}: ${activity.activity}\n`
        })
      })
    }
    
    return text
  }

  const handleGoBack = () => {
    if (currentView === 'results') {
      setCurrentView('form')
    } else if (currentView === 'generating') {
      resetGeneration()
      setCurrentView('form')
    } else if (currentView === 'api-setup') {
      setCurrentView('form')
    }
  }

  const handleStartOver = () => {
    resetGeneration()
    setCurrentView('form')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header with Navigation */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Trip Generation</h1>
              <div className="flex items-center gap-2 mt-2 text-sm text-gray-600">
                {/* Breadcrumb */}
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                  Step 1: Plan
                </span>
                <span className={currentView === 'generating' ? 'px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium' : ''}>
                  Step 2: Generate
                </span>
                <span className={currentView === 'results' ? 'px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium' : ''}>
                  Step 3: Review
                </span>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2">
              {currentView !== 'api-setup' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGoBack}
                  className="flex items-center gap-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back
                </Button>
              )}
              
              {currentView !== 'api-setup' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleStartOver}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Start Over
                </Button>
              )}
              
              {currentView !== 'api-setup' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowApiSetup(true)}
                  className="flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  API Settings
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* API Setup View */}
        {currentView === 'api-setup' && (
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                WanderWise API Access
              </h2>
              <p className="text-lg text-gray-600 mb-4">
                Generate API keys to integrate WanderWise travel planning into your applications.
              </p>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 max-w-2xl mx-auto mb-6">
                <p className="text-sm text-amber-700">
                  <strong>Note:</strong> API keys are for developers who want to integrate our service. 
                  Regular users can use the website directly without an API key!
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => setCurrentView('form')}
                className="mb-6"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Trip Planning
              </Button>
            </div>
            
            <APIKeyManager onKeyValid={handleApiKeyValidation} />
          </div>
        )}

        {/* API Setup Modal */}
        {showApiSetup && currentView !== 'api-setup' && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">API Settings</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowApiSetup(false)}
                >
                  ✕
                </Button>
              </div>
              <APIKeyManager onKeyValid={handleApiKeyValidation} />
            </div>
          </div>
        )}

        {/* Form View */}
        {currentView === 'form' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Plan Your Perfect Trip
              </h2>
              <p className="text-lg text-gray-600 mb-4">
                Tell us about your dream destination and preferences, and we&apos;ll create a personalized travel itinerary just for you.
              </p>
              
              {/* Developer API Access Notice */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-2xl mx-auto">
                <p className="text-sm text-blue-700 mb-2">
                  💡 <strong>Developers:</strong> Want to integrate travel planning into your app?
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentView('api-setup')}
                  className="text-blue-600 border-blue-300 hover:bg-blue-100"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Get API Access
                </Button>
              </div>
            </div>
            
            <TravelPlanningForm onSubmit={handleFormSubmit} />
          </div>
        )}

        {/* Generation Progress View */}
        {currentView === 'generating' && (
          <div className="max-w-4xl mx-auto">
            <GenerationProgress />
          </div>
        )}

        {/* Results View */}
        {currentView === 'results' && currentPlan && (
          <div className="max-w-6xl mx-auto">
            <TravelPlanResults
              plan={currentPlan}
              onSave={handleSavePlan}
              onShare={handleSharePlan}
              onDownload={handleDownloadPlan}
            />
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-red-900 mb-2">Generation Failed</h3>
              <p className="text-red-700 mb-4">{error}</p>
              <Button onClick={handleStartOver}>
                Try Again
              </Button>
            </div>
          </div>
        )}
      </div>

      <NotificationContainer />
    </div>
  )
}