'use client'

import { useState } from 'react'
import { usePlanManagementStore, SavedTravelPlan } from '../../lib/stores/plan-management-store'
import { useNotificationStore } from '../../lib/stores/notification-store'
import { TravelPlanResults } from '@/components/ui/travel-plan-results'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  X, 
  Heart, 
  Copy, 
  Trash2, 
  Tag, 
  Plus,
  Calendar,
  MapPin,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import Link from 'next/link'

interface PlanDetailPageProps {
  planId: string
}

export default function PlanDetailPage({ planId }: PlanDetailPageProps) {
  const {
    savedPlans,
    updatePlan,
    toggleFavorite,
    deletePlan,
    duplicatePlan,
    addPlanTags,
    removePlanTags,
    markAsViewed,
    getAllTags
  } = usePlanManagementStore()

  const { addNotification } = useNotificationStore()
  
  const plan = savedPlans.find(p => p.id === planId)
  
  const [isEditing, setIsEditing] = useState(false)
  const [editedName, setEditedName] = useState(plan?.name || '')
  const [editedNotes, setEditedNotes] = useState(plan?.notes || '')
  const [newTag, setNewTag] = useState('')
  const [showTagInput, setShowTagInput] = useState(false)

  const allTags = getAllTags()

  // Mark as viewed when component loads
  useState(() => {
    if (plan) {
      markAsViewed(planId)
    }
  })

  if (!plan) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Plan not found</h3>
            <p className="text-gray-600 mb-4">
              The travel plan you're looking for doesn't exist or has been deleted.
            </p>
            <Link href="/my-plans">
              <Button>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to My Plans
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleSave = () => {
    updatePlan(planId, {
      name: editedName,
      notes: editedNotes
    })
    setIsEditing(false)
    addNotification({
      type: 'success',
      title: 'Plan Updated',
      message: 'Your travel plan has been updated successfully.',
      duration: 3000
    })
  }

  const handleCancel = () => {
    setEditedName(plan.name)
    setEditedNotes(plan.notes || '')
    setIsEditing(false)
  }

  const handleToggleFavorite = () => {
    toggleFavorite(planId)
    addNotification({
      type: 'success',
      title: plan.is_favorite ? 'Removed from Favorites' : 'Added to Favorites',
      message: `${plan.name} ${plan.is_favorite ? 'removed from' : 'added to'} your favorites.`,
      duration: 3000
    })
  }

  const handleDuplicate = () => {
    const newId = duplicatePlan(planId)
    addNotification({
      type: 'success',
      title: 'Plan Duplicated',
      message: `Created a copy of "${plan.name}".`,
      duration: 3000
    })
    return newId
  }

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${plan.name}"?`)) {
      deletePlan(planId)
      addNotification({
        type: 'success',
        title: 'Plan Deleted',
        message: `${plan.name} has been deleted.`,
        duration: 3000
      })
      // Redirect to plans list
      window.location.href = '/my-plans'
    }
  }

  const handleAddTag = () => {
    if (newTag.trim() && !plan.tags.includes(newTag.trim())) {
      addPlanTags(planId, [newTag.trim()])
      setNewTag('')
      setShowTagInput(false)
      addNotification({
        type: 'success',
        title: 'Tag Added',
        message: `Added tag "${newTag.trim()}" to your plan.`,
        duration: 2000
      })
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    removePlanTags(planId, [tagToRemove])
    addNotification({
      type: 'success',
      title: 'Tag Removed',
      message: `Removed tag "${tagToRemove}" from your plan.`,
      duration: 2000
    })
  }

  const handleDownload = (planToDownload: any, format: 'json' | 'txt') => {
    const dataStr = JSON.stringify(planToDownload, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${plan.name.replace(/[^a-z0-9]/gi, '_')}-${plan.start_date}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(url)
    
    addNotification({
      type: 'success',
      title: 'Download Started',
      message: `Your travel plan is being downloaded as ${format.toUpperCase()}.`,
      duration: 3000
    })
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    addNotification({
      type: 'success',
      title: 'Link Copied',
      message: 'Shareable link copied to clipboard!',
      duration: 3000
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/my-plans">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Plans
                </Button>
              </Link>
              
              <div className="flex items-center gap-2">
                {isEditing ? (
                  <Input
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    className="text-xl font-bold"
                  />
                ) : (
                  <h1 className="text-2xl font-bold text-gray-900">{plan.name}</h1>
                )}
                
                {plan.is_favorite && (
                  <Heart className="w-5 h-5 text-red-500 fill-current" />
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isEditing ? (
                <>
                  <Button size="sm" onClick={handleSave} className="flex items-center gap-1">
                    <Save className="w-4 h-4" />
                    Save
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleCancel} className="flex items-center gap-1">
                    <X className="w-4 h-4" />
                    Cancel
                  </Button>
                </>
              ) : (
                <>
                  <Button size="sm" variant="outline" onClick={() => setIsEditing(true)} className="flex items-center gap-1">
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleToggleFavorite} className="flex items-center gap-1">
                    <Heart className={cn(
                      "w-4 h-4",
                      plan.is_favorite ? "text-red-500 fill-current" : "text-gray-400"
                    )} />
                    {plan.is_favorite ? 'Unfavorite' : 'Favorite'}
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleDuplicate} className="flex items-center gap-1">
                    <Copy className="w-4 h-4" />
                    Duplicate
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={handleDelete}
                    className="flex items-center gap-1 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Plan Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Plan Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="w-4 h-4 text-gray-400" />
                  <span>{plan.destination}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>{new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span>{plan.duration_days} days</span>
                </div>
                
                <div className="pt-2 border-t">
                  <div className="text-xs text-gray-500 space-y-1">
                    <div>Saved: {new Date(plan.saved_at).toLocaleDateString()}</div>
                    <div>Views: {plan.view_count}</div>
                    {plan.last_viewed && (
                      <div>Last viewed: {new Date(plan.last_viewed).toLocaleDateString()}</div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tags */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  <span>Tags</span>
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => setShowTagInput(!showTagInput)}
                    className="h-6 w-6 p-0"
                  >
                    <Plus className="w-3 h-3" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {showTagInput && (
                    <div className="flex gap-2">
                      <Input
                        placeholder="Add tag..."
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                        className="text-sm"
                      />
                      <Button size="sm" onClick={handleAddTag}>
                        Add
                      </Button>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-1">
                    {plan.tags.map((tag: string) => (
                      <Badge 
                        key={tag} 
                        variant="secondary" 
                        className="text-xs cursor-pointer flex items-center gap-1 group"
                      >
                        {tag}
                        <X 
                          className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => handleRemoveTag(tag)}
                        />
                      </Badge>
                    ))}
                    
                    {plan.tags.length === 0 && (
                      <p className="text-sm text-gray-500">No tags yet</p>
                    )}
                  </div>

                  {/* Suggested Tags */}
                  {allTags.length > 0 && showTagInput && (
                    <div>
                      <p className="text-xs font-medium text-gray-700 mb-2">Suggested:</p>
                      <div className="flex flex-wrap gap-1">
                        {allTags
                          .filter(tag => !plan.tags.includes(tag))
                          .slice(0, 5)
                          .map((tag: string) => (
                            <Badge 
                              key={tag} 
                              variant="outline" 
                              className="text-xs cursor-pointer"
                              onClick={() => {
                                addPlanTags(planId, [tag])
                                setShowTagInput(false)
                              }}
                            >
                              + {tag}
                            </Badge>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Notes */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Notes</CardTitle>
              </CardHeader>
              <CardContent>
                {isEditing ? (
                  <textarea
                    value={editedNotes}
                    onChange={(e) => setEditedNotes(e.target.value)}
                    placeholder="Add your notes about this trip..."
                    className="w-full min-h-[100px] p-3 border border-gray-300 rounded-md text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                ) : (
                  <p className="text-sm text-gray-600">
                    {plan.notes || 'No notes added yet.'}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <TravelPlanResults
              plan={plan}
              onSave={() => {}} // Already saved in management
              onShare={handleShare}
              onDownload={handleDownload}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
