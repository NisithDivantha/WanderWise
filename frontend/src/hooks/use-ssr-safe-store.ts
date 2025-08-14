'use client'

import { useEffect, useState } from 'react'

/**
 * SSR-safe store hook that prevents hydration mismatches
 * Returns initial values during SSR and actual values after hydration
 */
export function useSSRSafeStore<T>(
  hook: () => T,
  initialValue: T
): T {
  const [isClient, setIsClient] = useState(false)
  const [value, setValue] = useState(initialValue)

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (isClient) {
      setValue(hook())
    }
  }, [isClient, hook])

  if (!isClient) {
    return initialValue
  }

  return value
}
