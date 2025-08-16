import { create } from 'zustand'
import { TravelPlan, TravelPlanRequest, LoadingState } from '@/types/api'

export interface TravelPlanGenerationStep {
  id: string
  name: string
  description: string
  status: 'pending' | 'loading' | 'completed' | 'error'
  progress?: number
  message?: string
  error?: string
}

interface TravelPlanState {
  // Current generation state
  isGenerating: boolean
  currentRequest: TravelPlanRequest | null
  currentPlan: TravelPlan | null
  
  // Progress tracking
  generationSteps: TravelPlanGenerationStep[]
  currentStepIndex: number
  overallProgress: number
  
  // Error handling
  error: string | null
  
  // History
  planHistory: TravelPlan[]
  
  // Actions
  startGeneration: (request: TravelPlanRequest) => void
  updateStep: (stepId: string, updates: Partial<TravelPlanGenerationStep>) => void
  setCurrentStep: (stepIndex: number) => void
  completeGeneration: (plan: TravelPlan) => void
  failGeneration: (error: string) => void
  resetGeneration: () => void
  addToHistory: (plan: TravelPlan) => void
  clearHistory: () => void
}

const defaultSteps: TravelPlanGenerationStep[] = [
  {
    id: 'validation',
    name: 'Validating Request',
    description: 'Checking your travel preferences and requirements',
    status: 'pending',
    progress: 0
  },
  {
    id: 'destination',
    name: 'Analyzing Destination',
    description: 'Gathering information about your destination',
    status: 'pending',
    progress: 0
  },
  {
    id: 'poi',
    name: 'Finding Points of Interest',
    description: 'Discovering amazing places based on your interests',
    status: 'pending',
    progress: 0
  },
  {
    id: 'hotels',
    name: 'Finding Accommodations',
    description: 'Searching for the best hotels within your budget',
    status: 'pending',
    progress: 0
  },
  {
    id: 'itinerary',
    name: 'Creating Itinerary',
    description: 'Organizing your perfect day-by-day travel plan',
    status: 'pending',
    progress: 0
  },
  {
    id: 'optimization',
    name: 'Final Optimization',
    description: 'Fine-tuning your travel plan for the best experience',
    status: 'pending',
    progress: 0
  }
]

export const useTravelPlanStore = create<TravelPlanState>((set, get) => ({
  // Initial state
  isGenerating: false,
  currentRequest: null,
  currentPlan: null,
  generationSteps: [...defaultSteps],
  currentStepIndex: -1,
  overallProgress: 0,
  error: null,
  planHistory: [],

  // Actions
  startGeneration: (request) => {
    set({
      isGenerating: true,
      currentRequest: request,
      currentPlan: null,
      generationSteps: defaultSteps.map(step => ({ ...step, status: 'pending', progress: 0 })),
      currentStepIndex: 0,
      overallProgress: 0,
      error: null
    })
  },

  updateStep: (stepId, updates) => {
    set((state) => ({
      generationSteps: state.generationSteps.map(step =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    }))
    
    // Calculate overall progress
    const { generationSteps } = get()
    const totalProgress = generationSteps.reduce((sum, step) => sum + (step.progress || 0), 0)
    const overallProgress = Math.round(totalProgress / generationSteps.length)
    
    set({ overallProgress })
  },

  setCurrentStep: (stepIndex) => {
    set({ currentStepIndex: stepIndex })
    
    // Update step statuses
    set((state) => ({
      generationSteps: state.generationSteps.map((step, index) => ({
        ...step,
        status: index < stepIndex ? 'completed' : 
                index === stepIndex ? 'loading' : 'pending'
      }))
    }))
  },

  completeGeneration: (plan) => {
    set({
      isGenerating: false,
      currentPlan: plan,
      currentStepIndex: -1,
      overallProgress: 100,
      generationSteps: defaultSteps.map(step => ({ 
        ...step, 
        status: 'completed', 
        progress: 100 
      }))
    })
    
    // Add to history
    get().addToHistory(plan)
  },

  failGeneration: (error) => {
    set((state) => ({
      isGenerating: false,
      error,
      generationSteps: state.generationSteps.map(step => 
        step.status === 'loading' ? { ...step, status: 'error', error } : step
      )
    }))
  },

  resetGeneration: () => {
    set({
      isGenerating: false,
      currentRequest: null,
      currentPlan: null,
      generationSteps: [...defaultSteps],
      currentStepIndex: -1,
      overallProgress: 0,
      error: null
    })
  },

  addToHistory: (plan) => {
    set((state) => ({
      planHistory: [plan, ...state.planHistory].slice(0, 10) // Keep last 10 plans
    }))
  },

  clearHistory: () => {
    set({ planHistory: [] })
  }
}))
