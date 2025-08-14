import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { TravelPlan, TravelPlanRequest, LoadingState, NotificationState, APIKeyInfo } from '@/types/api'
import { generateId } from '@/lib/utils'

interface AppState {
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
}

// Create the store with SSR handling
export const useAppStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    // Loading state
    loading: { isLoading: false },
    setLoading: (loading) => set({ loading }),
    clearLoading: () => set({ loading: { isLoading: false } }),

    // Notifications
    notifications: [],
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
    apiKey: null,
    apiKeyInfo: null,
    setApiKey: (key) => set({ apiKey: key }),
    setApiKeyInfo: (info) => set({ apiKeyInfo: info }),
    clearApiKey: () => set({ apiKey: null, apiKeyInfo: null }),

    // Travel plans
    currentPlan: null,
    savedPlans: [],
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
    currentRequest: null,
    setCurrentRequest: (request) => set({ currentRequest: request }),

    // UI state
    sidebarOpen: false,
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    theme: 'light',
    setTheme: (theme) => set({ theme }),
  }))
)

// Convenience hooks for specific parts of the store
// Using individual selectors to avoid object recreation issues
export const useLoading = () => {
  const loading = useAppStore((state) => state.loading)
  const setLoading = useAppStore((state) => state.setLoading)
  const clearLoading = useAppStore((state) => state.clearLoading)
  
  return { loading, setLoading, clearLoading }
}

export const useNotifications = () => {
  const notifications = useAppStore((state) => state.notifications)
  const addNotification = useAppStore((state) => state.addNotification)
  const removeNotification = useAppStore((state) => state.removeNotification)
  const clearNotifications = useAppStore((state) => state.clearNotifications)
  
  return { notifications, addNotification, removeNotification, clearNotifications }
}

export const useApiKey = () => {
  const apiKey = useAppStore((state) => state.apiKey)
  const apiKeyInfo = useAppStore((state) => state.apiKeyInfo)
  const setApiKey = useAppStore((state) => state.setApiKey)
  const setApiKeyInfo = useAppStore((state) => state.setApiKeyInfo)
  const clearApiKey = useAppStore((state) => state.clearApiKey)
  
  return { apiKey, apiKeyInfo, setApiKey, setApiKeyInfo, clearApiKey }
}

export const useTravelPlans = () => {
  const currentPlan = useAppStore((state) => state.currentPlan)
  const savedPlans = useAppStore((state) => state.savedPlans)
  const setCurrentPlan = useAppStore((state) => state.setCurrentPlan)
  const savePlan = useAppStore((state) => state.savePlan)
  const removeSavedPlan = useAppStore((state) => state.removeSavedPlan)
  const clearSavedPlans = useAppStore((state) => state.clearSavedPlans)
  
  return { currentPlan, savedPlans, setCurrentPlan, savePlan, removeSavedPlan, clearSavedPlans }
}

export const useFormState = () => {
  const currentRequest = useAppStore((state) => state.currentRequest)
  const setCurrentRequest = useAppStore((state) => state.setCurrentRequest)
  
  return { currentRequest, setCurrentRequest }
}

export const useUI = () => {
  const sidebarOpen = useAppStore((state) => state.sidebarOpen)
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen)
  const theme = useAppStore((state) => state.theme)
  const setTheme = useAppStore((state) => state.setTheme)
  
  return { sidebarOpen, setSidebarOpen, theme, setTheme }
}
