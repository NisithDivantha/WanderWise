'use client'

import { Control, FieldErrors } from 'react-hook-form'
import { TravelFormData } from '@/lib/schemas/travel-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface Step3AdditionalOptionsProps {
  control: Control<TravelFormData>
  errors: FieldErrors<TravelFormData>
}

const ACCOMMODATION_OPTIONS = [
  { value: 'hotel' as const, label: '🏨 Hotels', description: 'Traditional hotels with full service' },
  { value: 'hostel' as const, label: '🛏️ Hostels', description: 'Budget-friendly shared accommodations' },
  { value: 'airbnb' as const, label: '🏠 Airbnb', description: 'Private rentals and unique stays' },
  { value: 'mixed' as const, label: '🔄 Mixed', description: 'Combination of different types' },
]

const TRANSPORTATION_OPTIONS = [
  { value: 'walking' as const, label: '🚶 Walking', description: 'Explore on foot' },
  { value: 'public' as const, label: '🚇 Public Transport', description: 'Buses, trains, metro' },
  { value: 'taxi' as const, label: '🚕 Taxi/Rideshare', description: 'Convenient door-to-door' },
  { value: 'rental' as const, label: '🚗 Car Rental', description: 'Freedom to explore' },
]

export function Step3AdditionalOptions({ control }: Step3AdditionalOptionsProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center text-sm font-semibold">
            3
          </span>
          Additional Options
        </CardTitle>
        <CardDescription>
          Fine-tune your trip with accommodation preferences and special requirements.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        {/* Accommodation Preference */}
        <FormField
          control={control}
          name="accommodation"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                🏠 Accommodation Preference (Optional)
              </FormLabel>
              <FormControl>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {ACCOMMODATION_OPTIONS.map((option) => (
                    <Button
                      key={option.value}
                      type="button"
                      variant={field.value === option.value ? "default" : "outline"}
                      className={cn(
                        "h-auto p-4 flex flex-col items-start gap-2 text-left transition-all duration-200",
                        field.value === option.value 
                          ? "bg-green-600 hover:bg-green-700 text-white border-green-600 ring-2 ring-green-200" 
                          : "hover:bg-green-50 hover:border-green-300"
                      )}
                      onClick={() => field.onChange(option.value)}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-base">{option.label}</span>
                      </div>
                      <span className={cn(
                        "text-sm",
                        field.value === option.value ? "text-green-100" : "text-muted-foreground"
                      )}>
                        {option.description}
                      </span>
                    </Button>
                  ))}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Transportation Preference */}
        <FormField
          control={control}
          name="transportation"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                🚗 Transportation Preference (Optional - Select multiple)
              </FormLabel>
              <FormControl>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {TRANSPORTATION_OPTIONS.map((option) => {
                    const isSelected = field.value?.includes(option.value) || false
                    return (
                      <Button
                        key={option.value}
                        type="button"
                        variant={isSelected ? "default" : "outline"}
                        className={cn(
                          "h-auto p-4 flex flex-col items-start gap-2 text-left transition-all duration-200",
                          isSelected
                            ? "bg-green-600 hover:bg-green-700 text-white border-green-600 ring-2 ring-green-200" 
                            : "hover:bg-green-50 hover:border-green-300"
                        )}
                        onClick={() => {
                          const currentValue = field.value || []
                          if (isSelected) {
                            // Remove the option
                            field.onChange(currentValue.filter((v: string) => v !== option.value))
                          } else {
                            // Add the option
                            field.onChange([...currentValue, option.value])
                          }
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-base">{option.label}</span>
                          {isSelected && (
                            <span className="ml-auto text-green-200">✓</span>
                          )}
                        </div>
                        <span className={cn(
                          "text-sm",
                          isSelected ? "text-green-100" : "text-muted-foreground"
                        )}>
                          {option.description}
                        </span>
                      </Button>
                    )
                  })}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Special Requirements */}
        <FormField
          control={control}
          name="specialRequirements"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                ✨ Special Requirements (Optional)
              </FormLabel>
              <FormControl>
                <textarea
                  placeholder="e.g., accessibility needs, dietary restrictions, special occasions..."
                  {...field}
                  className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </CardContent>
    </Card>
  )
}
