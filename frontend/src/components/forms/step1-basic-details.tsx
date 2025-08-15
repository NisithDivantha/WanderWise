'use client'

import { Control, FieldErrors } from 'react-hook-form'
import { TravelFormData } from '@/lib/schemas/travel-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface Step1BasicDetailsProps {
  control: Control<TravelFormData>
  errors: FieldErrors<TravelFormData>
}

export function Step1BasicDetails({ control }: Step1BasicDetailsProps) {
  // Get today's date in YYYY-MM-DD format for min date validation
  const today = new Date().toISOString().split('T')[0]
  
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="bg-primary text-primary-foreground rounded-full w-8 h-8 flex items-center justify-center text-sm font-semibold">
            1
          </span>
          Basic Trip Details
        </CardTitle>
        <CardDescription>
          Tell us where you want to go and when you&apos;re planning to travel.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Destination */}
        <FormField
          control={control}
          name="destination"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-base font-semibold">
                🌍 Destination
              </FormLabel>
              <FormControl>
                <Input
                  placeholder="e.g., Paris, France or Tokyo, Japan"
                  {...field}
                  className="text-lg"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Date Range */}
        <div className="space-y-2">
          <FormLabel className="text-base font-semibold">
            📅 Travel Dates
          </FormLabel>
          <p className="text-sm text-muted-foreground mb-3">
            Select your travel dates. You can plan trips up to 1 year in advance.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={control}
              name="startDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Start Date</FormLabel>
                  <FormControl>
                    <Input
                      type="date"
                      min={today}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={control}
              name="endDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>End Date</FormLabel>
                  <FormControl>
                    <Input
                      type="date"
                      min={today}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
