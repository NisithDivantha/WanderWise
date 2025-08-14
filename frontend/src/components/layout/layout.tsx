'use client'

import React, { useState, useEffect } from 'react'
import { Header } from './header'
import { Footer } from './footer'
import { NotificationContainer } from '@/components/ui/notification-container'
import { ClientOnly } from '@/components/client-only'
import { useUI } from '@/lib/stores/app-store'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isClient, setIsClient] = useState(false)
  const { theme } = useUI()

  useEffect(() => {
    setIsClient(true)
  }, [])

  return (
    <div className={`min-h-screen flex flex-col ${isClient && theme === 'dark' ? 'dark' : ''}`}>
      <Header />
      
      <main className="flex-1 bg-gray-50">
        {children}
      </main>
      
      <Footer />
      
      {/* Global Notifications - Client Only */}
      <ClientOnly>
        <NotificationContainer />
      </ClientOnly>
    </div>
  )
}

export { Layout }
