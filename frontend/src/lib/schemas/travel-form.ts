import { z } from 'zod'

// Form validation schema
export const travelFormSchema = z.object({
  // Step 1: Basic Trip Details
  destination: z.string().min(2, 'Destination must be at least 2 characters'),
  startDate: z.string().min(1, 'Start date is required').refine((date) => {
    const selectedDate = new Date(date)
    const today = new Date()
    today.setHours(0, 0, 0, 0) // Reset to start of today
    return selectedDate >= today
  }, 'Start date must be today or in the future'),
  endDate: z.string().min(1, 'End date is required').refine((date) => {
    const selectedDate = new Date(date)
    const today = new Date()
    today.setHours(0, 0, 0, 0) // Reset to start of today
    return selectedDate >= today
  }, 'End date must be today or in the future'),
  
  // Step 2: Trip Preferences  
  budget: z.enum(['budget', 'mid-range', 'luxury'], {
    message: 'Please select a budget range'
  }),
  interests: z.array(z.string()).min(1, 'Select at least one interest'),
  travelStyle: z.enum(['relaxed', 'moderate', 'packed'], {
    message: 'Please select a travel style'
  }),
  
  // Step 3: Additional Options
  accommodation: z.enum(['hotel', 'hostel', 'airbnb', 'mixed']).optional(),
  transportation: z.array(z.enum(['walking', 'public', 'taxi', 'rental'])).optional(),
  specialRequirements: z.string().optional(),
}).refine((data) => {
  const start = new Date(data.startDate)
  const end = new Date(data.endDate)
  return end > start
}, {
  message: "End date must be after start date",
  path: ["endDate"],
}).refine((data) => {
  // Additional validation: trip length shouldn't be too long (optional)
  const start = new Date(data.startDate)
  const end = new Date(data.endDate)
  const diffInDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
  return diffInDays <= 365 // Max 1 year trip
}, {
  message: "Trip duration cannot exceed 1 year",
  path: ["endDate"],
})

export type TravelFormData = z.infer<typeof travelFormSchema>

// Individual step schemas for validation
export const step1Schema = travelFormSchema.pick({
  destination: true,
  startDate: true,
  endDate: true,
})

export const step2Schema = travelFormSchema.pick({
  budget: true,
  interests: true,
  travelStyle: true,
})

export const step3Schema = travelFormSchema.pick({
  accommodation: true,
  transportation: true,
  specialRequirements: true,
})

export type Step1Data = z.infer<typeof step1Schema>
export type Step2Data = z.infer<typeof step2Schema>
export type Step3Data = z.infer<typeof step3Schema>

// Interest options
export const INTEREST_OPTIONS = [
  { value: 'culture', label: '🏛️ Culture & History', description: 'Museums, historical sites, local traditions' },
  { value: 'food', label: '🍽️ Food & Dining', description: 'Local cuisine, restaurants, food tours' },
  { value: 'nature', label: '🌿 Nature & Outdoors', description: 'Parks, hiking, natural landmarks' },
  { value: 'nightlife', label: '🌃 Nightlife & Entertainment', description: 'Bars, clubs, live music' },
  { value: 'shopping', label: '🛍️ Shopping', description: 'Markets, boutiques, local crafts' },
  { value: 'adventure', label: '🎯 Adventure Sports', description: 'Extreme sports, adrenaline activities' },
  { value: 'relaxation', label: '🧘 Relaxation & Wellness', description: 'Spas, beaches, peaceful spots' },
  { value: 'art', label: '🎨 Art & Architecture', description: 'Galleries, street art, iconic buildings' },
] as const

// Budget options
export const BUDGET_OPTIONS = [
  {
    value: 'budget' as const,
    label: 'Budget',
    description: 'Affordable options, hostels, local food',
    icon: '💰'
  },
  {
    value: 'mid-range' as const,
    label: 'Mid-Range',
    description: 'Comfortable hotels, good restaurants',
    icon: '💎'
  },
  {
    value: 'luxury' as const,
    label: 'Luxury',
    description: 'Premium hotels, fine dining, exclusive experiences',
    icon: '👑'
  },
] as const

// Travel style options
export const TRAVEL_STYLE_OPTIONS = [
  {
    value: 'relaxed' as const,
    label: 'Relaxed',
    description: 'Take it slow, plenty of downtime',
    icon: '🌅'
  },
  {
    value: 'moderate' as const,
    label: 'Moderate',
    description: 'Balanced mix of activities and rest',
    icon: '⚖️'
  },
  {
    value: 'packed' as const,
    label: 'Packed',
    description: 'See everything, maximize activities',
    icon: '⚡'
  },
] as const
