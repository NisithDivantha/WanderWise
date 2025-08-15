'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { TravelFormData, travelFormSchema } from '@/lib/schemas/travel-form'
import { Form } from '@/components/ui/form'
import { Button } from '@/components/ui/button'
import { Step1BasicDetails } from './step1-basic-details'
import { Step2Preferences } from './step2-preferences'
import { Step3AdditionalOptions } from './step3-additional-options'
import { CheckCircle2, Loader2 } from 'lucide-react'

interface TravelPlanningFormProps {
  onSubmit: (data: TravelFormData) => Promise<void>
}

const steps = [
  {
    id: 'basic-details',
    title: 'Basic Details',
    description: 'Destination and dates',
  },
  {
    id: 'preferences',
    title: 'Preferences',
    description: 'Budget and interests',
  },
  {
    id: 'options',
    title: 'Additional Options',
    description: 'Accommodation and special needs',
  },
]

export function TravelPlanningForm({ onSubmit }: TravelPlanningFormProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<TravelFormData>({
    resolver: zodResolver(travelFormSchema),
    defaultValues: {
      destination: '',
      startDate: '',
      endDate: '',
      budget: 'mid-range',
      interests: [],
      travelStyle: 'moderate',
      accommodation: undefined,
      transportation: [],
      specialRequirements: '',
    },
  })

  const { control, handleSubmit, formState: { errors }, trigger, watch } = form

  const validateStep = async (step: number) => {
    switch (step) {
      case 0:
        return await trigger(['destination', 'startDate', 'endDate'])
      case 1:
        return await trigger(['budget', 'interests', 'travelStyle'])
      case 2:
        // Step 3 fields are all optional, so validation should always pass
        return true
      default:
        return true
    }
  }

  const handleNext = async () => {
    console.log('handleNext called, currentStep:', currentStep)
    const isValid = await validateStep(currentStep)
    console.log('Step validation result:', isValid)
    if (isValid && currentStep < steps.length - 1) {
      console.log('Moving to next step:', currentStep + 1)
      setCurrentStep(currentStep + 1)
    } else {
      console.log('Cannot move to next step. Valid:', isValid, 'Current step:', currentStep, 'Max step:', steps.length - 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFormSubmit = async (data: TravelFormData) => {
    console.log('handleFormSubmit called, currentStep:', currentStep, 'steps.length - 1:', steps.length - 1)
    
    // Only allow submission on the last step
    if (currentStep !== steps.length - 1) {
      console.log('Form submission prevented - not on last step')
      return
    }
    
    console.log('Proceeding with form submission')
    setIsSubmitting(true)
    try {
      await onSubmit(data)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStep = () => {
    console.log('renderStep called, currentStep:', currentStep)
    switch (currentStep) {
      case 0:
        return <Step1BasicDetails control={control} errors={errors} />
      case 1:
        return <Step2Preferences control={control} errors={errors} />
      case 2:
        return <Step3AdditionalOptions control={control} errors={errors} />
      default:
        return null
    }
  }

  const formData = watch()
  const isStepComplete = (stepIndex: number) => {
    let result = false
    switch (stepIndex) {
      case 0:
        result = !!(formData.destination && formData.startDate && formData.endDate)
        break
      case 1:
        result = !!(formData.budget && formData.interests?.length > 0 && formData.travelStyle)
        break
      case 2:
        result = true // This step is optional
        break
      default:
        result = false
    }
    console.log('isStepComplete for step', stepIndex, ':', result, formData)
    return result
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-center mb-2">
          ✈️ Plan Your Perfect Trip
        </h1>
        <p className="text-center text-muted-foreground mb-6">
          Tell us about your travel preferences and we&apos;ll create a personalized itinerary for you
        </p>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    index < currentStep
                      ? 'bg-green-500 text-white'
                      : index === currentStep
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {index < currentStep ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    index + 1
                  )}
                </div>
                <div className="mt-2 text-center">
                  <div className="text-xs font-semibold">{step.title}</div>
                  <div className="text-xs text-muted-foreground">{step.description}</div>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`w-16 h-0.5 mx-4 ${
                    index < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <Form {...form}>
      <Form {...form}>
        <div>
          {renderStep()}

          {/* Navigation */}
          <div className="flex justify-between items-center mt-8 max-w-4xl mx-auto">
            <Button
              type="button"
              variant="outline"
              onClick={handlePrev}
              disabled={currentStep === 0}
            >
              Previous
            </Button>

            <div className="text-sm text-muted-foreground">
              Step {currentStep + 1} of {steps.length}
            </div>

            {currentStep < steps.length - 1 ? (
              <Button
                type="button"
                onClick={handleNext}
                disabled={!isStepComplete(currentStep)}
              >
                Next
              </Button>
            ) : currentStep === steps.length - 1 ? (
              <Button
                type="button"
                onClick={() => {
                  console.log('Submit button clicked')
                  handleSubmit(handleFormSubmit)()
                }}
                disabled={isSubmitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Your Trip...
                  </>
                ) : (
                  'Create My Trip Plan'
                )}
              </Button>
            ) : (
              <div>Error: Invalid step</div>
            )}
          </div>
        </div>
      </Form>
      </Form>
    </div>
  )
}
