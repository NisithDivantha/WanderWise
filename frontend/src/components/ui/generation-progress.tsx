'use client'

import { useTravelPlanStore } from '@/lib/stores/travel-plan-store'
import { CheckCircle2, Loader2, AlertCircle, Circle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GenerationProgressProps {
  className?: string
}

export function GenerationProgress({ className }: GenerationProgressProps) {
  const { 
    isGenerating, 
    generationSteps, 
    currentStepIndex, 
    overallProgress,
    error 
  } = useTravelPlanStore()

  if (!isGenerating && !error && overallProgress === 0) {
    return null
  }

  const getStepIcon = (step: typeof generationSteps[0], index: number) => {
    if (step.status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />
    }
    
    if (step.status === 'loading') {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
    }
    
    if (step.status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-500" />
    }
    
    return <Circle className="w-5 h-5 text-gray-300" />
  }

  const getStepStatus = (step: typeof generationSteps[0]) => {
    switch (step.status) {
      case 'completed':
        return 'text-green-600'
      case 'loading':
        return 'text-blue-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  return (
    <div className={cn("w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg", className)}>
      {/* Overall Progress Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            {error ? 'Generation Failed' : isGenerating ? 'Creating Your Travel Plan' : 'Generation Complete'}
          </h3>
          <span className="text-sm font-medium text-gray-600">
            {overallProgress}%
          </span>
        </div>
        
        {/* Overall Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={cn(
              "h-2 rounded-full transition-all duration-300",
              error ? "bg-red-500" : overallProgress === 100 ? "bg-green-500" : "bg-blue-500"
            )}
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <div>
              <h4 className="text-red-800 font-medium">Generation Failed</h4>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Step Details */}
      <div className="space-y-4">
        {generationSteps.map((step, index) => (
          <div 
            key={step.id} 
            className={cn(
              "flex items-start space-x-3 p-3 rounded-lg transition-all duration-200",
              step.status === 'loading' && "bg-blue-50 border border-blue-200",
              step.status === 'completed' && "bg-green-50 border border-green-200",
              step.status === 'error' && "bg-red-50 border border-red-200"
            )}
          >
            {/* Step Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {getStepIcon(step, index)}
            </div>
            
            {/* Step Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className={cn("font-medium", getStepStatus(step))}>
                  {step.name}
                </h4>
                {step.progress !== undefined && step.progress > 0 && (
                  <span className="text-xs text-gray-500">
                    {step.progress}%
                  </span>
                )}
              </div>
              
              <p className="text-sm text-gray-600 mt-1">
                {step.message || step.description}
              </p>
              
              {/* Individual Step Progress Bar */}
              {step.status === 'loading' && step.progress !== undefined && (
                <div className="mt-2 w-full bg-gray-200 rounded-full h-1">
                  <div 
                    className="h-1 bg-blue-500 rounded-full transition-all duration-300"
                    style={{ width: `${step.progress}%` }}
                  />
                </div>
              )}
              
              {/* Error Message for Step */}
              {step.error && (
                <p className="text-sm text-red-600 mt-1">
                  Error: {step.error}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Fun Loading Messages */}
      {isGenerating && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-center">
            <Loader2 className="w-6 h-6 text-blue-500 animate-spin mx-auto mb-2" />
            <p className="text-blue-700 font-medium">
              {getLoadingMessage(currentStepIndex)}
            </p>
            <p className="text-blue-600 text-sm mt-1">
              This may take a few moments while we craft the perfect trip for you...
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

// Fun loading messages to keep users engaged
function getLoadingMessage(stepIndex: number): string {
  const messages = [
    "🔍 Analyzing your travel preferences...",
    "🗺️ Exploring your destination...",
    "🎯 Finding amazing attractions just for you...",
    "🏨 Searching for perfect accommodations...",
    "📅 Crafting your day-by-day itinerary...",
    "✨ Adding final touches to your plan..."
  ]
  
  return messages[stepIndex] || "🚀 Working on something amazing..."
}
