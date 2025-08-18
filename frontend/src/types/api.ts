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
  rating: number;
  description?: string;
  category?: string;
  address?: string;
  opening_hours?: string;
  price_level?: number;
  coordinates?: {
    lat?: number;
    lng?: number;
  };
}

export interface Hotel {
  name: string;
  price?: string;
  rating?: number;
  description?: string;
  price_range?: string;
  address?: string;
  amenities?: string[];
  booking_url?: string;
}

export interface ItineraryDay {
  date: string;
  day?: number;
  theme?: string;
  activities: Activity[];
  estimated_budget?: string;
}

export interface Activity {
  time: string;
  activity: string;
  description?: string;
  location?: string;
  duration?: string;
  notes?: string;
}

export interface TravelPlanSummary {
  theme?: string;
  estimated_budget?: string;
  highlights?: string[];
  travel_tips?: string[];
}

export interface TravelPlan {
  destination: string;
  start_date: string;
  end_date: string;
  executive_summary: string;
  points_of_interest: PointOfInterest[];
  hotels: Hotel[];
  itinerary: ItineraryDay[];
  generation_timestamp: string;
  file_paths: Record<string, string>;
  
  // Optional summary data (may be derived from executive_summary)
  summary?: TravelPlanSummary;
  
  // Computed properties for compatibility
  duration_days?: number;
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
