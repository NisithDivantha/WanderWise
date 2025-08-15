'use client'

import { Control, FieldErrors } from 'react-hook-form'
import { TravelFormData, BUDGET_OPTIONS, INTEREST_OPTIONS, TRAVEL_STYLE_OPTIONS } from '@/lib/schemas/travel-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface Step2PreferencesProps {
  control: Control<TravelFormData>
  errors: FieldErrors<TravelFormData>
}

export function Step2Preferences({ control }: Step2PreferencesProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center text-sm font-semibold">
            2
          </span>
          Travel Preferences
        </CardTitle>
        <CardDescription>
          Help us personalize your trip by telling us about your preferences and interests.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        {/* Budget Selection */}
        <FormField
          control={control}
          name="budget"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                💰 Budget Range
              </FormLabel>
              <FormControl>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {BUDGET_OPTIONS.map((option) => (
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
                        <span className="text-xl">{option.icon}</span>
                        <span className="font-semibold">{option.label}</span>
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

        {/* Travel Style Selection */}
        <FormField
          control={control}
          name="travelStyle"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                🎯 Travel Style
              </FormLabel>
              <FormControl>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {TRAVEL_STYLE_OPTIONS.map((option) => (
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
                        <span className="text-xl">{option.icon}</span>
                        <span className="font-semibold">{option.label}</span>
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

        {/* Interests Selection */}
        <FormField
          control={control}
          name="interests"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                ❤️ Interests (Select all that apply)
              </FormLabel>
              <FormControl>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {INTEREST_OPTIONS.map((option) => (
                    <Button
                      key={option.value}
                      type="button"
                      variant={field.value?.includes(option.value) ? "default" : "outline"}
                      className={cn(
                        "h-auto p-4 flex flex-col items-start gap-2 text-left transition-all duration-200",
                        field.value?.includes(option.value)
                          ? "bg-green-600 hover:bg-green-700 text-white border-green-600 ring-2 ring-green-200" 
                          : "hover:bg-green-50 hover:border-green-300"
                      )}
                      onClick={() => {
                        const currentInterests = field.value || []
                        if (currentInterests.includes(option.value)) {
                          field.onChange(currentInterests.filter(i => i !== option.value))
                        } else {
                          field.onChange([...currentInterests, option.value])
                        }
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-base">{option.label}</span>
                      </div>
                      <span className={cn(
                        "text-sm",
                        field.value?.includes(option.value) ? "text-green-100" : "text-muted-foreground"
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
      </CardContent>
    </Card>
  )
}
