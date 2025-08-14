import { createStore } from 'zustand/vanilla'
import { TravelPlan, TravelPlanRequest, LoadingState, NotificationState, APIKeyInfo } from '@/types/api'
import { generateId } from '@/lib/utils'

export interface AppState {
  // Loading state
  loading: LoadingState
  setLoading: (loading: LoadingState) => void
  clearLoading: () => void

  // Notifications
  notifications: NotificationState[]
  addNotification: (notification: Omit<NotificationState, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // API Key management
  apiKey: string | null
  apiKeyInfo: APIKeyInfo | null
  setApiKey: (key: string) => void
  setApiKeyInfo: (info: APIKeyInfo | null) => void
  clearApiKey: () => void

  // Travel plans
  currentPlan: TravelPlan | null
  savedPlans: TravelPlan[]
  setCurrentPlan: (plan: TravelPlan | null) => void
  savePlan: (plan: TravelPlan) => void
  removeSavedPlan: (planId: string) => void
  clearSavedPlans: () => void

  // Form state
  currentRequest: TravelPlanRequest | null
  setCurrentRequest: (request: TravelPlanRequest | null) => void

  // UI state
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
  
  // Hydration flag for SSR
  _hasHydrated: boolean
  setHasHydrated: (state: boolean) => void
}

const initialState = {
  loading: { isLoading: false },
  notifications: [],
  apiKey: null,
  apiKeyInfo: null,
  currentPlan: null,
  savedPlans: [],
  currentRequest: null,
  sidebarOpen: false,
  theme: 'light' as const,
  _hasHydrated: false,
}

export type AppStore = ReturnType<typeof createAppStore>

export const createAppStore = () => {
  return createStore<AppState>()((set, get) => ({
    ...initialState,
    
    // Loading state
    setLoading: (loading) => set({ loading }),
    clearLoading: () => set({ loading: { isLoading: false } }),

    // Notifications
    addNotification: (notification) => {
      const newNotification: NotificationState = {
        ...notification,
        id: generateId(),
        timestamp: Date.now(),
      }
      set((state) => ({
        notifications: [...state.notifications, newNotification],
      }))

      // Auto-remove notification after duration
      if (notification.duration !== 0) {
        const duration = notification.duration || 5000
        setTimeout(() => {
          get().removeNotification(newNotification.id)
        }, duration)
      }
    },
    removeNotification: (id) =>
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      })),
    clearNotifications: () => set({ notifications: [] }),

    // API Key management
    setApiKey: (key) => set({ apiKey: key }),
    setApiKeyInfo: (info) => set({ apiKeyInfo: info }),
    clearApiKey: () => set({ apiKey: null, apiKeyInfo: null }),

    // Travel plans
    setCurrentPlan: (plan) => set({ currentPlan: plan }),
    savePlan: (plan) => {
      const planWithId = {
        ...plan,
        plan_id: plan.plan_id || generateId(),
      }
      set((state) => {
        const existingIndex = state.savedPlans.findIndex(
          (p) => p.plan_id === planWithId.plan_id
        )
        if (existingIndex >= 0) {
          // Update existing plan
          const updatedPlans = [...state.savedPlans]
          updatedPlans[existingIndex] = planWithId
          return { savedPlans: updatedPlans }
        } else {
          // Add new plan
          return { savedPlans: [...state.savedPlans, planWithId] }
        }
      })
    },
    removeSavedPlan: (planId) =>
      set((state) => ({
        savedPlans: state.savedPlans.filter((p) => p.plan_id !== planId),
      })),
    clearSavedPlans: () => set({ savedPlans: [] }),

    // Form state
    setCurrentRequest: (request) => set({ currentRequest: request }),

    // UI state
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    setTheme: (theme) => set({ theme }),
    
    // Hydration
    setHasHydrated: (state) => set({ _hasHydrated: state }),
  }))
}
