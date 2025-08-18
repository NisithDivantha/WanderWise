'use client'

import { TravelPlan } from '@/types/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from './badge'
import { 
  MapPin, 
  Calendar, 
  Clock, 
  DollarSign, 
  Star, 
  Hotel, 
  Camera,
  Share2,
  Download,
  Heart,
  ExternalLink
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

interface TravelPlanResultsProps {
  plan: TravelPlan
  onSave?: (plan: TravelPlan) => void
  onShare?: (plan: TravelPlan) => void
  onDownload?: (plan: TravelPlan, format: 'json' | 'txt') => void
  className?: string
}

export function TravelPlanResults({ 
  plan, 
  onSave, 
  onShare, 
  onDownload, 
  className 
}: TravelPlanResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'itinerary' | 'places' | 'hotels'>('overview')
  const [savedPlans, setSavedPlans] = useState<Set<string>>(new Set())

  const handleSave = () => {
    if (onSave) {
      onSave(plan)
      setSavedPlans(prev => new Set([...prev, plan.plan_id || '']))
    }
  }

  const isSaved = plan.plan_id ? savedPlans.has(plan.plan_id) : false

  const tabs = [
    { id: 'overview', label: 'Overview', icon: MapPin },
    { id: 'itinerary', label: 'Itinerary', icon: Calendar },
    { id: 'places', label: 'Places', icon: Camera },
    { id: 'hotels', label: 'Hotels', icon: Hotel }
  ] as const

  return (
    <div className={cn("w-full max-w-6xl mx-auto", className)}>
      {/* Header */}
      <div className="mb-6 p-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              ✈️ Your {plan.destination} Adventure
            </h1>
            <div className="flex flex-wrap items-center gap-4 text-blue-100">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{plan.duration_days} days</span>
              </div>
              <div className="flex items-center gap-1">
                <DollarSign className="w-4 h-4" />
                <span>{plan.summary?.estimated_budget || 'Budget varies'}</span>
              </div>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex gap-2 mt-4 md:mt-0">
            <Button 
              variant="secondary"
              size="sm"
              onClick={handleSave}
              className="flex items-center gap-1"
            >
              <Heart className={cn("w-4 h-4", isSaved && "fill-current text-red-500")} />
              {isSaved ? 'Saved' : 'Save'}
            </Button>
            
            {onShare && (
              <Button 
                variant="secondary"
                size="sm"
                onClick={() => onShare(plan)}
                className="flex items-center gap-1"
              >
                <Share2 className="w-4 h-4" />
                Share
              </Button>
            )}
            
            {onDownload && (
              <Button 
                variant="secondary"
                size="sm"
                onClick={() => onDownload(plan, 'json')}
                className="flex items-center gap-1"
              >
                <Download className="w-4 h-4" />
                Export
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
              activeTab === tab.id
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && <OverviewTab plan={plan} />}
        {activeTab === 'itinerary' && <ItineraryTab plan={plan} />}
        {activeTab === 'places' && <PlacesTab plan={plan} />}
        {activeTab === 'hotels' && <HotelsTab plan={plan} />}
      </div>
    </div>
  )
}

// Overview Tab Component
function OverviewTab({ plan }: { plan: TravelPlan }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Trip Summary */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Trip Highlights
          </CardTitle>
          <CardDescription>
            {plan.summary?.theme || plan.executive_summary}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {plan.summary?.highlights?.length ? (
              plan.summary.highlights.map((highlight: string, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </span>
                  <p className="text-gray-700">{highlight}</p>
                </div>
              ))
            ) : (
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-gray-700">{plan.executive_summary}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Duration:</span>
              <span className="font-medium">{plan.duration_days} days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Places to visit:</span>
              <span className="font-medium">{plan.points_of_interest.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Hotel options:</span>
              <span className="font-medium">{plan.hotels.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Budget:</span>
              <span className="font-medium">{plan.summary?.estimated_budget || 'Budget varies'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Travel Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {plan.summary?.travel_tips?.length ? (
                plan.summary.travel_tips.slice(0, 3).map((tip: string, index: number) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0 mt-2"></span>
                    {tip}
                  </li>
                ))
              ) : (
                <li className="text-sm text-gray-600">
                  General travel tips will be included in your detailed itinerary.
                </li>
              )}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// Itinerary Tab Component  
function ItineraryTab({ plan }: { plan: TravelPlan }) {
  return (
    <div className="space-y-6">
      {plan.itinerary.map((day, index) => (
        <Card key={day.day || day.date}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {day.day || new Date(day.date).getDate()}
              </span>
              Day {day.day || new Date(day.date).getDate()} - {new Date(day.date).toLocaleDateString()}
            </CardTitle>
            {day.theme && (
              <CardDescription>
                Theme: {day.theme}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {day.activities.map((activity, actIndex) => (
                <div key={actIndex} className="flex items-start gap-4 p-3 border-l-2 border-blue-200 bg-gray-50 rounded-r-lg">
                  <div className="flex-shrink-0">
                    <Badge variant="outline" className="text-xs">
                      {activity.time}
                    </Badge>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{activity.activity}</h4>
                    <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                      <MapPin className="w-3 h-3" />
                      {activity.location || ''}
                    </p>
                    {activity.duration && (
                      <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3" />
                        {activity.duration}
                      </p>
                    )}
                    {activity.notes && (
                      <p className="text-sm text-gray-600 mt-1">{activity.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {day.estimated_budget && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-green-700">
                  <DollarSign className="w-4 h-4 inline mr-1" />
                  Estimated budget for today: {day.estimated_budget}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Places Tab Component
function PlacesTab({ plan }: { plan: TravelPlan }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {plan.points_of_interest.map((poi, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader>
            <CardTitle className="text-lg flex items-start justify-between">
              <span>{poi.name}</span>
              <div className="flex items-center gap-1 text-yellow-500">
                <Star className="w-4 h-4 fill-current" />
                <span className="text-sm font-medium text-gray-600">{poi.rating}</span>
              </div>
            </CardTitle>
            <CardDescription>
              <Badge variant="secondary" className="text-xs">
                {poi.category || 'Attraction'}
              </Badge>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-3 overflow-hidden max-h-16" 
               style={{ 
                 display: '-webkit-box',
                 WebkitLineClamp: 3,
                 WebkitBoxOrient: 'vertical'
               }}>
              {poi.description}
            </p>
            <div className="space-y-2 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                <span>{poi.address || 'Address not available'}</span>
              </div>
              {poi.opening_hours && (
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{poi.opening_hours}</span>
                </div>
              )}
              {poi.price_level && (
                <div className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3" />
                  <span>{'$'.repeat(poi.price_level || 1)} Price Level</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Hotels Tab Component  
function HotelsTab({ plan }: { plan: TravelPlan }) {
  return (
    <div className="space-y-6">
      {plan.hotels.map((hotel, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{hotel.name}</span>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 text-yellow-500">
                  <Star className="w-4 h-4 fill-current" />
                  <span className="text-sm font-medium text-gray-600">{hotel.rating}</span>
                </div>
                <Badge variant="outline">{hotel.price_range || hotel.price || 'Price varies'}</Badge>
              </div>
            </CardTitle>
            <CardDescription className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {hotel.address || 'Address not available'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">{hotel.description}</p>
            
            {/* Amenities */}
            {hotel.amenities && hotel.amenities.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">Amenities</h4>
                <div className="flex flex-wrap gap-1">
                  {hotel.amenities.slice(0, 6).map((amenity: string, idx: number) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {amenity}
                    </Badge>
                  ))}
                  {hotel.amenities.length > 6 && (
                    <Badge variant="outline" className="text-xs">
                      +{hotel.amenities.length - 6} more
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* Booking Link */}
            {hotel.booking_url && (
              <Button 
                variant="outline" 
                size="sm" 
                className="flex items-center gap-2"
                onClick={() => hotel.booking_url && window.open(hotel.booking_url, '_blank')}
              >
                <ExternalLink className="w-4 h-4" />
                View Details & Book
              </Button>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
