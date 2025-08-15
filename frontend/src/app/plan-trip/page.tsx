'use client'

import { useState } from 'react'
import { TravelFormData } from '@/lib/schemas/travel-form'
import { TravelPlanningForm } from '@/components/forms/travel-planning-form'
import { useNotifications } from '@/lib/stores/notifications'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

export default function PlanTripPage() {
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submittedData, setSubmittedData] = useState<TravelFormData | null>(null)
  const { addNotification } = useNotifications()

  const handleFormSubmit = async (data: TravelFormData) => {
    try {
      // Here you would normally send the data to your backend API
      console.log('Travel form submitted:', data)
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Add success notification
      addNotification({
        type: 'success',
        title: 'Trip Planning Request Submitted!',
        message: `We're creating your perfect itinerary for ${data.destination}`,
        duration: 6000
      })
      
      setSubmittedData(data)
      setIsSubmitted(true)
    } catch (error) {
      console.error('Error submitting travel form:', error)
      addNotification({
        type: 'error',
        title: 'Submission Failed',
        message: 'There was an error submitting your trip request. Please try again.',
        duration: 8000
      })
      throw error
    }
  }

  if (isSubmitted && submittedData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 py-8">
        <div className="container mx-auto px-4">
          <Card className="max-w-2xl mx-auto">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl text-green-600">
                Trip Planning Request Submitted!
              </CardTitle>
              <CardDescription>
                We&apos;re working on creating your perfect itinerary for {submittedData.destination}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Your Trip Details:</h3>
                <div className="space-y-1 text-sm">
                  <p><strong>Destination:</strong> {submittedData.destination}</p>
                  <p><strong>Dates:</strong> {submittedData.startDate} to {submittedData.endDate}</p>
                  <p><strong>Budget:</strong> {submittedData.budget}</p>
                  <p><strong>Travel Style:</strong> {submittedData.travelStyle}</p>
                  <p><strong>Interests:</strong> {submittedData.interests.join(', ')}</p>
                </div>
              </div>
              
              <div className="text-center space-y-4">
                <p className="text-sm text-muted-foreground">
                  You&apos;ll receive your personalized itinerary within the next few minutes.
                </p>
                <Link href="/">
                  <Button>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Home
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/">
            <Button variant="ghost">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </Link>
        </div>
        
        <TravelPlanningForm onSubmit={handleFormSubmit} />
      </div>
    </div>
  )
}
