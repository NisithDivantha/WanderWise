'use client'

import { useRef } from 'react'
import { TravelPlan } from '@/types/api'
import dynamic from 'next/dynamic'

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { 
  ssr: false,
  loading: () => <div className="w-full h-96 bg-gray-100 animate-pulse rounded-lg flex items-center justify-center">Loading map...</div>
})

const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false })
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false })

interface TravelMapProps {
  plan: TravelPlan
  className?: string
  height?: string
}

export function TravelMap({ plan, className = '', height = '400px' }: TravelMapProps) {
  const mapRef = useRef<any>(null)

  // Get all coordinates from POIs and hotels
  const getAllCoordinates = () => {
    const coords: Array<{ lat: number; lng: number; name: string; type: 'poi' | 'hotel' }> = []
    
    // Add POI coordinates
    plan.points_of_interest.forEach((poi: any) => {
      if (poi.coordinates?.lat && poi.coordinates?.lng) {
        coords.push({
          lat: poi.coordinates.lat,
          lng: poi.coordinates.lng,
          name: poi.name,
          type: 'poi'
        })
      }
    })

    // Add hotel coordinates (if available)
    plan.hotels.forEach((hotel: any) => {
      // For now, we'll use default coordinates based on destination
      // In a real implementation, you'd geocode the hotel addresses
    })

    return coords
  }

  // Get center coordinates (default to a major city if no coordinates available)
  const getCenterCoordinates = () => {
    const coords = getAllCoordinates()
    if (coords.length > 0) {
      const lat = coords.reduce((sum, coord) => sum + coord.lat, 0) / coords.length
      const lng = coords.reduce((sum, coord) => sum + coord.lng, 0) / coords.length
      return { lat, lng }
    }

    // Default coordinates for popular destinations
    const defaultCoords: Record<string, { lat: number; lng: number }> = {
      'paris': { lat: 48.8566, lng: 2.3522 },
      'london': { lat: 51.5074, lng: -0.1278 },
      'tokyo': { lat: 35.6762, lng: 139.6503 },
      'rome': { lat: 41.9028, lng: 12.4964 },
      'new york': { lat: 40.7128, lng: -74.0060 },
      'barcelona': { lat: 41.3851, lng: 2.1734 }
    }

    const destination = plan.destination.toLowerCase()
    for (const [city, coords] of Object.entries(defaultCoords)) {
      if (destination.includes(city)) {
        return coords
      }
    }

    // Default to Paris if no match
    return { lat: 48.8566, lng: 2.3522 }
  }

  const center = getCenterCoordinates()
  const coordinates = getAllCoordinates()

  // Custom marker icons
  const createCustomIcon = (type: 'poi' | 'hotel') => {
    if (typeof window === 'undefined') return undefined
    
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const L = require('leaflet')
    
    return L.divIcon({
      className: 'custom-marker',
      html: `
        <div class="relative">
          <div class="w-8 h-8 rounded-full ${type === 'poi' ? 'bg-blue-500' : 'bg-red-500'} border-2 border-white shadow-lg flex items-center justify-center">
            ${type === 'poi' ? 
              '<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2L3 7v11h14V7l-7-5z"/></svg>' :
              '<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a4 4 0 00-4 4v4.54l4 7.46 4-7.46V6a4 4 0 00-4-4z"/></svg>'
            }
          </div>
          <div class="absolute top-full left-1/2 transform -translate-x-1/2">
            <div class="w-2 h-2 ${type === 'poi' ? 'bg-blue-500' : 'bg-red-500'} rotate-45 -mt-1"></div>
          </div>
        </div>
      `,
      iconSize: [32, 40],
      iconAnchor: [16, 40],
      popupAnchor: [0, -40]
    })
  }

  return (
    <div className={`w-full ${className}`} style={{ height }}>
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={coordinates.length > 0 ? 12 : 10}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
        ref={mapRef}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {coordinates.map((coord, index) => (
          <Marker
            key={index}
            position={[coord.lat, coord.lng]}
            icon={createCustomIcon(coord.type)}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-medium">{coord.name}</div>
                <div className="text-gray-500 capitalize">{coord.type === 'poi' ? 'Point of Interest' : 'Hotel'}</div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}

// Fallback component for when map data isn't available
export function MapPlaceholder({ plan, className = '', height = '400px' }: TravelMapProps) {
  return (
    <div className={`w-full bg-gray-100 rounded-lg flex items-center justify-center ${className}`} style={{ height }}>
      <div className="text-center text-gray-500">
        <div className="text-lg mb-2">📍</div>
        <div className="text-sm font-medium">Map for {plan.destination}</div>
        <div className="text-xs">Interactive map coming soon</div>
      </div>
    </div>
  )
}
