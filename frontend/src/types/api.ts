// Shared types for WanderWise Travel Planner API

export interface TravelPlanRequest {
  destination: string;
  start_date: string;
  end_date: string;
  interests?: string[];
  budget?: 'low' | 'medium' | 'high';
  group_size?: number;
}

export interface PointOfInterest {
  name: string;
  description: string;
  rating: number;
  address: string;
  category: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  opening_hours?: string;
  price_level?: number;
  photos?: string[];
}

export interface Hotel {
  name: string;
  rating: number;
  price_range: string;
  address: string;
  amenities: string[];
  description: string;
  booking_url?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  photos?: string[];
}

export interface ItineraryDay {
  day: number;
  date: string;
  activities: Activity[];
  theme?: string;
  estimated_budget?: string;
}

export interface Activity {
  time: string;
  activity: string;
  location: string;
  duration?: string;
  notes?: string;
  category?: string;
}

export interface TravelPlan {
  destination: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  points_of_interest: PointOfInterest[];
  hotels: Hotel[];
  itinerary: ItineraryDay[];
  summary: {
    theme: string;
    highlights: string[];
    estimated_budget: string;
    best_time_to_visit: string;
    travel_tips: string[];
  };
  generated_at: string;
  plan_id?: string;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface APIError {
  detail: string;
  status_code: number;
  timestamp: string;
}

// Form validation types
export interface FormErrors {
  [key: string]: string | undefined;
}

// UI State types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
}

// API Key types (matching backend)
export interface APIKeyInfo {
  key_id: string;
  name: string;
  created_at: string;
  last_used?: string;
  rate_limit: number;
  is_active: boolean;
}

export interface APIKeyGenerationRequest {
  name: string;
  rate_limit?: number;
}

export interface APIKeyGenerationResponse {
  api_key: string;
  key_info: APIKeyInfo;
}
