'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useApiKey, useUI } from '@/lib/stores/app-store'

const Header: React.FC = () => {
  const [isClient, setIsClient] = useState(false)
  const { apiKey, apiKeyInfo } = useApiKey()
  const { theme, setTheme, sidebarOpen, setSidebarOpen } = useUI()

  useEffect(() => {
    setIsClient(true)
  }, [])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo and Brand */}
        <div className="flex items-center space-x-4">
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-600 text-white font-bold">
              W
            </div>
            <span className="text-xl font-bold text-gray-900">WanderWise</span>
          </Link>
          <span className="text-sm text-gray-500 hidden sm:block">AI Travel Planner</span>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <Link 
            href="/" 
            className="text-gray-700 hover:text-blue-600 transition-colors"
          >
            Home
          </Link>
          <Link 
            href="/plans" 
            className="text-gray-700 hover:text-blue-600 transition-colors"
          >
            My Plans
          </Link>
          <Link 
            href="/destinations" 
            className="text-gray-700 hover:text-blue-600 transition-colors"
          >
            Destinations
          </Link>
        </nav>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          {/* API Key Status */}
          <div className="hidden sm:flex items-center space-x-2">
            {isClient && apiKey ? (
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Connected</span>
                {apiKeyInfo && (
                  <span className="text-xs text-gray-400">
                    ({apiKeyInfo.name})
                  </span>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm text-gray-600">No API Key</span>
              </div>
            )}
          </div>

          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="hidden sm:flex"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </Button>

          {/* API Key Setup */}
          <Link href="/setup">
            <Button variant={apiKey ? "outline" : "default"} size="sm">
              {apiKey ? "Settings" : "Setup API"}
            </Button>
          </Link>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </Button>
        </div>
      </div>
    </header>
  )
}

export { Header }
