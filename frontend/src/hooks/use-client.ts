import { useEffect, useState } from 'react'

/**
 * Custom hook to handle client-side only state
 * Prevents SSR hydration mismatches
 */
export function useIsClient() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  return isClient
}

/**
 * Safe hook for using stores that might cause SSR issues
 * Returns initial values during SSR and actual values on client
 * Uses simple client detection for reliability
 */
export function useClientOnly<T>(hook: () => T, fallback: T): T {
  const isClient = useIsClient()
  
  if (!isClient) {
    return fallback
  }
  
  return hook()
}
