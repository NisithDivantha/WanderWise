'use client'

import { useState } from 'react'
import { TravelFormData } from '@/lib/schemas/travel-form'
import { TravelPlanningForm } from '@/components/forms/travel-planning-form'
import { GenerationProgress } from '@/components/ui/generation-progress'
import { TravelPlanResults } from '@/components/ui/travel-plan-results'
import { NotificationContainer } from '@/components/ui/notification-container'
import { useTravelPlanStore } from '@/lib/stores/travel-plan-store'
import { usePlanManagementStore } from '../../lib/stores/plan-management-store'
import { tripGenerationService } from '@/lib/services/trip-generation'
import { TravelPlanRequest, TravelPlan } from '@/types/api'
import { Button } from '@/components/ui/button'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import { useNotificationStore } from '../../lib/stores/notification-store'

export default function TripGenerationPage() {
  const [currentView, setCurrentView] = useState<'form' | 'generating' | 'results'>('form')
  
  const { 
    isGenerating, 
    currentPlan, 
    error, 
    resetGeneration 
  } = useTravelPlanStore()
  
  const { savePlan } = usePlanManagementStore()
  const { addNotification } = useNotificationStore()

  const handleFormSubmit = async (formData: TravelFormData) => {
    try {
      // Convert form data to API request format
      const request: TravelPlanRequest = {
        destination: formData.destination,
        start_date: formData.startDate,
        end_date: formData.endDate,
        interests: formData.interests,
        budget: formData.budget as 'low' | 'medium' | 'high',
        group_size: 1 // Default for now
      }

      // Switch to generation view
      setCurrentView('generating')

      // Start the generation process
      const result = await tripGenerationService.generateTravelPlan(request)

      // Switch to results view
      setCurrentView('results')

      // Automatically save the plan
      const planName = `${result.destination} Adventure`
      const savedPlanId = savePlan(result, planName)

      // Show success notification
      addNotification({
        type: 'success',
        title: 'Trip Generated & Saved!',
        message: `Your ${result.duration_days}-day ${result.destination} adventure is ready and saved to your plans.`,
        duration: 5000
      })

    } catch (error) {
      console.error('Trip generation failed:', error)
      
      // Show error notification
      addNotification({
        type: 'error',
        title: 'Generation Failed',
        message: error instanceof Error ? error.message : 'Something went wrong. Please try again.',
        duration: 8000
      })

      // Stay on generation view to show error state
    }
  }

  const handleStartOver = () => {
    resetGeneration()
    setCurrentView('form')
    
    addNotification({
      type: 'info',
      title: 'Starting Fresh',
      message: 'Ready to plan your next adventure!',
      duration: 3000
    })
  }

  const handleSavePlan = (plan: TravelPlan) => {
    // In a real app, this would save to user account or local storage
    addNotification({
      type: 'success',
      title: 'Plan Saved',
      message: 'Your travel plan has been saved to your account.',
      duration: 3000
    })
  }

  const handleSharePlan = (plan: TravelPlan) => {
    // In a real app, this would generate a shareable link
    navigator.clipboard.writeText(window.location.href)
    
    addNotification({
      type: 'success',
      title: 'Link Copied',
      message: 'Shareable link copied to clipboard!',
      duration: 3000
    })
  }

  const handleDownloadPlan = async (plan: TravelPlan, format: 'json' | 'txt') => {
    try {
      // In a real app, this would call the download API
      const dataStr = JSON.stringify(plan, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `travel-plan-${plan.destination}-${plan.start_date}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      
      addNotification({
        type: 'success',
        title: 'Download Started',
        message: `Your travel plan is being downloaded as ${format.toUpperCase()}.`,
        duration: 3000
      })
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Download Failed',
        message: 'Could not download the travel plan. Please try again.',
        duration: 5000
      })
    }
  }

  const handleGoBack = () => {
    if (currentView === 'results') {
      setCurrentView('generating')
    } else if (currentView === 'generating') {
      setCurrentView('form')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">
                ✈️ WanderWise
              </h1>
              
              {/* Navigation breadcrumbs */}
              <div className="hidden sm:flex items-center gap-2 text-sm text-gray-500">
                <span className={currentView === 'form' ? 'text-blue-600 font-medium' : ''}>
                  Plan
                </span>
                {currentView !== 'form' && (
                  <>
                    <span>→</span>
                    <span className={currentView === 'generating' ? 'text-blue-600 font-medium' : ''}>
                      Generate
                    </span>
                  </>
                )}
                {currentView === 'results' && (
                  <>
                    <span>→</span>
                    <span className="text-blue-600 font-medium">Results</span>
                  </>
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2">
              {currentView !== 'form' && (
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
              
              {(currentView === 'generating' || currentView === 'results') && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleStartOver}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Start Over
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'form' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Plan Your Perfect Trip
              </h2>
              <p className="text-lg text-gray-600">
                Tell us about your dream destination and preferences, and we'll create a personalized travel itinerary just for you.
              </p>
            </div>
            
            <TravelPlanningForm onSubmit={handleFormSubmit} />
          </div>
        )}

        {currentView === 'generating' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Creating Your Adventure
              </h2>
              <p className="text-lg text-gray-600">
                Sit back and relax while we craft the perfect travel plan for you. This won't take long!
              </p>
            </div>
            
            <GenerationProgress />
            
            {error && (
              <div className="mt-8 text-center">
                <Button onClick={handleStartOver} className="flex items-center gap-2 mx-auto">
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </Button>
              </div>
            )}
          </div>
        )}

        {currentView === 'results' && currentPlan && (
          <div>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Your Adventure Awaits! 🎉
              </h2>
              <p className="text-lg text-gray-600">
                Here's your personalized travel plan. You can save, share, or download it anytime.
              </p>
            </div>
            
            <TravelPlanResults
              plan={currentPlan}
              onSave={handleSavePlan}
              onShare={handleSharePlan}
              onDownload={handleDownloadPlan}
            />
          </div>
        )}
      </main>

      {/* Notifications */}
      <NotificationContainer />
    </div>
  )
}
