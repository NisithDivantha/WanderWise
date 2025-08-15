'use client'

import React, { useState } from 'react'
import { DayPicker, DateRange } from 'react-day-picker'
import { format, differenceInDays } from 'date-fns'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import 'react-day-picker/dist/style.css'

interface DateRangePickerProps {
  startDate?: string
  endDate?: string
  onDateChange: (startDate: string, endDate: string) => void
  className?: string
  error?: string
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onDateChange,
  className,
  error
}) => {
  const [showCalendar, setShowCalendar] = useState(false)
  const [selectedRange, setSelectedRange] = useState<DateRange | undefined>(
    startDate && endDate
      ? { from: new Date(startDate), to: new Date(endDate) }
      : undefined
  )

  const handleSelect = (range: DateRange | undefined) => {
    setSelectedRange(range)
    
    if (range?.from && range?.to) {
      onDateChange(
        format(range.from, 'yyyy-MM-dd'),
        format(range.to, 'yyyy-MM-dd')
      )
      setShowCalendar(false)
    }
  }

  const getTripDuration = () => {
    if (selectedRange?.from && selectedRange?.to) {
      const days = differenceInDays(selectedRange.to, selectedRange.from)
      return `${days + 1} day${days !== 0 ? 's' : ''}`
    }
    return null
  }

  const formatDateRange = () => {
    if (selectedRange?.from && selectedRange?.to) {
      return `${format(selectedRange.from, 'MMM dd')} - ${format(selectedRange.to, 'MMM dd, yyyy')}`
    } else if (selectedRange?.from) {
      return format(selectedRange.from, 'MMM dd, yyyy')
    }
    return 'Select dates'
  }

  return (
    <div className={cn('relative', className)}>
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Travel Dates
        </label>
        
        {/* Date Display Button */}
        <Button
          type="button"
          variant="outline"
          className={cn(
            'w-full justify-start text-left font-normal h-12',
            !selectedRange?.from && 'text-gray-400',
            error && 'border-red-500 focus:border-red-500'
          )}
          onClick={() => setShowCalendar(!showCalendar)}
        >
          <div className="flex items-center justify-between w-full">
            <span>📅 {formatDateRange()}</span>
            {getTripDuration() && (
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {getTripDuration()}
              </span>
            )}
          </div>
        </Button>

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
      </div>

      {/* Calendar Popup */}
      {showCalendar && (
        <div className="absolute top-full left-0 z-50 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <DayPicker
            mode="range"
            selected={selectedRange}
            onSelect={handleSelect}
            disabled={{ before: new Date() }}
            numberOfMonths={2}
            className="rdp-custom"
            modifiersStyles={{
              selected: {
                backgroundColor: '#3B82F6',
                color: 'white',
              },
              range_start: {
                backgroundColor: '#1D4ED8',
              },
              range_end: {
                backgroundColor: '#1D4ED8',
              },
              range_middle: {
                backgroundColor: '#DBEAFE',
                color: '#1E40AF',
              },
            }}
          />
          
          <div className="mt-4 flex justify-between items-center border-t pt-4">
            <div className="text-sm text-gray-600">
              {selectedRange?.from && selectedRange?.to && (
                <>
                  <strong>{getTripDuration()}</strong> trip
                </>
              )}
            </div>
            <div className="space-x-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedRange(undefined)
                  onDateChange('', '')
                }}
              >
                Clear
              </Button>
              <Button
                type="button"
                size="sm"
                onClick={() => setShowCalendar(false)}
                disabled={!selectedRange?.from || !selectedRange?.to}
              >
                Done
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Backdrop to close calendar */}
      {showCalendar && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowCalendar(false)}
        />
      )}
    </div>
  )
}
