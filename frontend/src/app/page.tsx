'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { useApiKey } from '@/lib/stores/app-store'

export default function Home() {
  const [isClient, setIsClient] = useState(false)
  const { apiKey } = useApiKey()

  useEffect(() => {
    setIsClient(true)
  }, [])

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
            Plan Your Perfect Trip with{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI-Powered Intelligence
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            WanderWise uses advanced AI agents to create personalized travel itineraries tailored to your interests, 
            budget, and preferences. Discover amazing destinations and experiences effortlessly.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link href="/trip-generation">
            <Button size="lg" className="text-lg px-8 py-4">
              🚀 Plan Your Trip
            </Button>
          </Link>
          
          <Link href="/destinations">
            <Button variant="outline" size="lg" className="text-lg px-8 py-4">
              Browse Destinations
            </Button>
          </Link>
        </div>

        {/* API Status */}
        <div className="flex justify-center">
          {isClient && apiKey ? (
            <div className="flex items-center space-x-2 text-green-600 bg-green-50 px-4 py-2 rounded-full">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium">API Connected - Ready to plan!</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-yellow-600 bg-yellow-50 px-4 py-2 rounded-full">
              <div className="h-2 w-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium">Setup required - Click &ldquo;Get Started&rdquo; to configure your API key</span>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-20 grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <div className="text-center space-y-4 p-6 rounded-lg bg-white border border-gray-200 shadow-sm">
          <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">AI-Powered Planning</h3>
          <p className="text-gray-600">
            Our intelligent agents analyze your preferences to create personalized itineraries with the best attractions, restaurants, and activities.
          </p>
        </div>

        <div className="text-center space-y-4 p-6 rounded-lg bg-white border border-gray-200 shadow-sm">
          <div className="mx-auto w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Local Insights</h3>
          <p className="text-gray-600">
            Get recommendations for hidden gems, local favorites, and must-visit attractions based on real traveler reviews and expert knowledge.
          </p>
        </div>

        <div className="text-center space-y-4 p-6 rounded-lg bg-white border border-gray-200 shadow-sm">
          <div className="mx-auto w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Smart Scheduling</h3>
          <p className="text-gray-600">
            Optimize your time with intelligent day-by-day itineraries that consider travel distances, opening hours, and your energy levels.
          </p>
        </div>
      </div>

      {/* How it Works */}
      <div className="mt-20 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How WanderWise Works</h2>
        <div className="space-y-8">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">1</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Tell us your destination and dates</h3>
              <p className="text-gray-600">Simply enter where you want to go and when you are traveling.</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">2</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Share your interests and preferences</h3>
              <p className="text-gray-600">Let us know what you love - culture, food, nature, nightlife, or adventure.</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">3</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Get your personalized itinerary</h3>
              <p className="text-gray-600">Our AI creates a detailed day-by-day plan with recommendations, timing, and tips.</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="mt-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">Ready to Start Your Adventure?</h2>
        <p className="text-lg mb-8 opacity-90">
          Join thousands of travelers who have discovered their perfect trips with WanderWise.
        </p>
        {isClient && apiKey ? (
          <Link href="/plan">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-4">
              Create Your First Trip
            </Button>
          </Link>
        ) : (
          <Link href="/setup">
            <Button size="lg" variant="secondary" className="text-lg px-8 py-4">
              Setup Your Account
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}
