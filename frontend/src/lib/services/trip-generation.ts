import { apiClient } from '../api/client'
import { TravelPlanRequest, TravelPlan } from '@/types/api'
import { useTravelPlanStore } from '@/lib/stores/travel-plan-store'

export class TripGenerationService {
  private static instance: TripGenerationService
  
  public static getInstance(): TripGenerationService {
    if (!TripGenerationService.instance) {
      TripGenerationService.instance = new TripGenerationService()
    }
    return TripGenerationService.instance
  }

  /**
   * Generate travel plan with real-time progress updates
   */
  async generateTravelPlan(request: TravelPlanRequest): Promise<TravelPlan> {
    const store = useTravelPlanStore.getState()
    
    try {
      // Start the generation process
      store.startGeneration(request)
      
      // Start progress updates in background (non-blocking)
      const progressPromise = this.simulateProgressUpdates()
      
      // Convert form data to API format
      const apiRequest: TravelPlanRequest = {
        destination: request.destination,
        start_date: request.start_date,
        end_date: request.end_date,
        interests: request.interests,
        budget: this.mapBudgetToAPI(request.budget),
        group_size: 1 // Default for now, can be made configurable
      }
      
      // Check if we have an API key to determine which endpoint to use
      const hasApiKey = typeof window !== 'undefined' && localStorage.getItem('wanderwise_api_key')
      
      // Make the actual API call (this is the real backend call)
      const result = hasApiKey 
        ? await apiClient.generateTravelPlan(apiRequest)
        : await apiClient.generateTravelPlanPublic(apiRequest)
      
      // Ensure progress simulation completes
      await progressPromise
      
      // Complete the generation
      store.completeGeneration(result)
      
      return result
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      store.failGeneration(errorMessage)
      throw error
    }
  }

  /**
   * Simulate real-time progress updates for better UX
   */
  private async simulateProgressUpdates(): Promise<void> {
    const store = useTravelPlanStore.getState()
    const steps = store.generationSteps
    
    for (let stepIndex = 0; stepIndex < steps.length; stepIndex++) {
      const step = steps[stepIndex]
      
      // Set current step
      store.setCurrentStep(stepIndex)
      
      // Simulate progress for this step
      await this.simulateStepProgress(step.id, stepIndex)
      
      // Mark step as completed
      store.updateStep(step.id, { 
        status: 'completed', 
        progress: 100,
        message: this.getCompletionMessage(step.id)
      })
      
      // Small delay between steps
      await this.delay(300)
    }
  }

  /**
   * Simulate progress within a single step
   */
  private async simulateStepProgress(stepId: string, stepIndex: number): Promise<void> {
    const store = useTravelPlanStore.getState()
    
    // Different steps take different amounts of time
    const stepDurations = [500, 800, 1200, 1000, 1500, 800] // milliseconds
    const duration = stepDurations[stepIndex] || 1000
    
    const progressSteps = 20
    const intervalTime = duration / progressSteps
    
    for (let i = 0; i <= progressSteps; i++) {
      const progress = Math.round((i / progressSteps) * 100)
      
      store.updateStep(stepId, {
        status: 'loading',
        progress,
        message: this.getProgressMessage(stepId, progress)
      })
      
      await this.delay(intervalTime)
    }
  }

  /**
   * Get progress message for a step
   */
  private getProgressMessage(stepId: string, progress: number): string {
    const messages: Record<string, string[]> = {
      validation: [
        "Checking your travel dates...",
        "Validating destination...",
        "Processing your preferences..."
      ],
      destination: [
        "Researching your destination...",
        "Gathering local insights...",
        "Analyzing travel conditions..."
      ],
      poi: [
        "Discovering hidden gems...",
        "Finding popular attractions...",
        "Matching places to your interests..."
      ],
      hotels: [
        "Searching accommodation options...",
        "Comparing hotels and prices...",
        "Finding the best deals..."
      ],
      itinerary: [
        "Planning your daily activities...",
        "Optimizing travel routes...",
        "Creating the perfect schedule..."
      ],
      optimization: [
        "Fine-tuning your plan...",
        "Adding final touches...",
        "Preparing your results..."
      ]
    }
    
    const stepMessages = messages[stepId] || ["Processing..."]
    const messageIndex = Math.floor((progress / 100) * (stepMessages.length - 1))
    return stepMessages[messageIndex]
  }

  /**
   * Get completion message for a step
   */
  private getCompletionMessage(stepId: string): string {
    const messages: Record<string, string> = {
      validation: "✅ Request validated successfully",
      destination: "✅ Destination analysis complete", 
      poi: "✅ Amazing places discovered",
      hotels: "✅ Perfect accommodations found",
      itinerary: "✅ Itinerary crafted to perfection",
      optimization: "✅ Your travel plan is ready!"
    }
    
    return messages[stepId] || "✅ Step completed"
  }

  /**
   * Map form budget to API budget format
   */
  private mapBudgetToAPI(budget?: string): 'low' | 'medium' | 'high' {
    switch (budget) {
      case 'budget':
        return 'low'
      case 'mid-range':
        return 'medium'
      case 'luxury':
        return 'high'
      default:
        return 'medium'
    }
  }

  /**
   * Utility function for delays
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Get generation history
   */
  getGenerationHistory(): TravelPlan[] {
    return useTravelPlanStore.getState().planHistory
  }

  /**
   * Clear generation history
   */
  clearHistory(): void {
    useTravelPlanStore.getState().clearHistory()
  }

  /**
   * Reset current generation state
   */
  resetGeneration(): void {
    useTravelPlanStore.getState().resetGeneration()
  }
}

// Export singleton instance
export const tripGenerationService = TripGenerationService.getInstance()
