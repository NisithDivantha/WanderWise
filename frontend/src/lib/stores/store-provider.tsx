'use client'

import React, { createContext, useContext, useRef, useEffect, useState } from 'react'
import { useStore } from 'zustand'
import { createAppStore, type AppStore } from './app-store-new'

const StoreContext = createContext<AppStore | null>(null)

export const StoreProvider = ({ children }: { children: React.ReactNode }) => {
  const storeRef = useRef<AppStore | null>(null)
  const [isHydrated, setIsHydrated] = useState(false)

  if (!storeRef.current) {
    storeRef.current = createAppStore()
  }

  useEffect(() => {
    setIsHydrated(true)
    if (storeRef.current) {
      storeRef.current.getState().setHasHydrated(true)
    }
  }, [])

  return (
    <StoreContext.Provider value={storeRef.current}>
      <div suppressHydrationWarning={!isHydrated}>
        {children}
      </div>
    </StoreContext.Provider>
  )
}

export const useAppContext = () => {
  const store = useContext(StoreContext)
  if (!store) {
    throw new Error('useAppContext must be used within StoreProvider')
  }
  return store
}

// SSR-safe hooks
export const useAppStore = <T,>(selector: (state: any) => T, fallback?: T): T => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  try {
    const value = useStore(store, selector)
    
    if (!isClient && fallback !== undefined) {
      return fallback
    }
    
    return value
  } catch {
    return fallback as T
  }
}

// Convenience hooks for specific parts of the store
export const useLoading = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      loading: { isLoading: false },
      setLoading: () => {},
      clearLoading: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    loading: state.loading,
    setLoading: state.setLoading,
    clearLoading: state.clearLoading,
  }))
}

export const useNotifications = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      notifications: [],
      addNotification: () => {},
      removeNotification: () => {},
      clearNotifications: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    notifications: state.notifications,
    addNotification: state.addNotification,
    removeNotification: state.removeNotification,
    clearNotifications: state.clearNotifications,
  }))
}

export const useApiKey = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      apiKey: null,
      apiKeyInfo: null,
      setApiKey: () => {},
      setApiKeyInfo: () => {},
      clearApiKey: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    apiKey: state.apiKey,
    apiKeyInfo: state.apiKeyInfo,
    setApiKey: state.setApiKey,
    setApiKeyInfo: state.setApiKeyInfo,
    clearApiKey: state.clearApiKey,
  }))
}

export const useTravelPlans = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      currentPlan: null,
      savedPlans: [],
      setCurrentPlan: () => {},
      savePlan: () => {},
      removeSavedPlan: () => {},
      clearSavedPlans: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    currentPlan: state.currentPlan,
    savedPlans: state.savedPlans,
    setCurrentPlan: state.setCurrentPlan,
    savePlan: state.savePlan,
    removeSavedPlan: state.removeSavedPlan,
    clearSavedPlans: state.clearSavedPlans,
  }))
}

export const useFormState = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      currentRequest: null,
      setCurrentRequest: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    currentRequest: state.currentRequest,
    setCurrentRequest: state.setCurrentRequest,
  }))
}

export const useUI = () => {
  const store = useAppContext()
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  if (!isClient) {
    return {
      sidebarOpen: false,
      setSidebarOpen: () => {},
      theme: 'light' as const,
      setTheme: () => {}
    }
  }
  
  return useStore(store, (state) => ({
    sidebarOpen: state.sidebarOpen,
    setSidebarOpen: state.setSidebarOpen,
    theme: state.theme,
    setTheme: state.setTheme,
  }))
}
