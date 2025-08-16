'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { usePlanManagementStore } from '../../../lib/stores/plan-management-store'
import { useNotificationStore } from '../../../lib/stores/notification-store'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Edit, Share2, Download, Copy, Trash2, Heart } from 'lucide-react'
import PlanDetailComponent from '../../../components/plans/plan-detail'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export default function PlanDetailPage() {
  const params = useParams()
  const router = useRouter()
  const planId = params.id as string
  
  const {
    savedPlans,
    updatePlan,
    duplicatePlan,
    deletePlan,
    toggleFavorite
  } = usePlanManagementStore()
  
  const { addNotification } = useNotificationStore()
  
  const plan = savedPlans.find(p => p.id === planId)
  
  useEffect(() => {
    if (plan) {
      // Increment view count when plan is viewed
      updatePlan(planId, { view_count: (plan.view_count || 0) + 1 })
    }
  }, [planId, plan, updatePlan])
  
  const handleUpdatePlan = (updates: any) => {
    if (!plan) return
    
    updatePlan(planId, updates)
    addNotification({
      type: 'success',
      title: 'Success',
      message: 'Plan updated successfully'
    })
  }
  
  const handleDuplicate = () => {
    if (!plan) return
    
    const duplicatedId = duplicatePlan(planId)
    addNotification({
      type: 'success',
      title: 'Success',
      message: 'Plan duplicated successfully'
    })
    router.push(`/my-plans/${duplicatedId}`)
  }
  
  const handleDelete = () => {
    if (!plan) return
    
    if (window.confirm('Are you sure you want to delete this plan? This action cannot be undone.')) {
      deletePlan(planId)
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Plan deleted successfully'
      })
      router.push('/my-plans')
    }
  }
  
  const handleToggleFavorite = () => {
    if (!plan) return
    
    toggleFavorite(planId)
    addNotification({
      type: 'success',
      title: 'Success',
      message: plan.is_favorite ? 'Removed from favorites' : 'Added to favorites'
    })
  }
  
  const handleShare = () => {
    // In a real app, this would generate a shareable link or open a share dialog
    const shareUrl = `${window.location.origin}/my-plans/${planId}`
    navigator.clipboard.writeText(shareUrl)
    addNotification({
      type: 'success',
      title: 'Success',
      message: 'Plan link copied to clipboard'
    })
  }
  
  const handleDownload = () => {
    if (!plan) return
    
    // Create a JSON file with the plan data
    const dataStr = JSON.stringify(plan, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `${plan.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_travel_plan.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    addNotification({
      type: 'success',
      title: 'Success',
      message: 'Plan downloaded successfully'
    })
  }
  
  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Plan Not Found</h1>
            <p className="text-gray-600 mb-8">The plan you're looking for doesn't exist or has been deleted.</p>
            <Link href="/my-plans">
              <Button>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to My Plans
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/my-plans">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Plans
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{plan.name}</h1>
                <p className="text-sm text-gray-500">{plan.destination} • {plan.duration_days} days</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleToggleFavorite}
                className={cn(
                  plan.is_favorite && "text-red-600 hover:text-red-700"
                )}
              >
                <Heart className={cn(
                  "w-4 h-4 mr-2",
                  plan.is_favorite ? "fill-current" : ""
                )} />
                {plan.is_favorite ? 'Favorited' : 'Favorite'}
              </Button>
              
              <Button variant="ghost" size="sm" onClick={handleShare}>
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              
              <Button variant="ghost" size="sm" onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
              
              <Button variant="ghost" size="sm" onClick={handleDuplicate}>
                <Copy className="w-4 h-4 mr-2" />
                Duplicate
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PlanDetailComponent
          planId={planId}
        />
      </main>
    </div>
  )
}
