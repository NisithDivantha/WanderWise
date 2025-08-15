'use client'

import { ReactNode } from 'react'

interface FormStep {
  id: string
  title: string
  description: string
  component: ReactNode
}

interface FormWizardProps {
  steps: FormStep[]
  currentStep: number
  onNext: () => void
  onPrev: () => void
  onSubmit?: () => void
}

export function FormWizard({ steps, currentStep, onNext, onPrev, onSubmit }: FormWizardProps) {
  const current = steps[currentStep]

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Current step content */}
      <div className="mb-8">
        {current.component}
      </div>
    </div>
  )
}
