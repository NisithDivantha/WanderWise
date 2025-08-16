'use client'

import { useState, useEffect } from 'react'
import { usePlanManagementStore } from '../../lib/stores/plan-management-store'
import { useNotificationStore } from '../../lib/stores/notification-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  Plus, 
  Grid, 
  List, 
  Filter, 
  SortAsc, 
  SortDesc,
  Heart,
  Folder,
  Tag,
  MoreVertical,
  Edit,
  Copy,
  Trash2,
  Star,
  Calendar,
  MapPin,
  Clock,
  Eye
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import Link from 'next/link'
import { FolderManager } from '../../components/plans/folder-manager'

export default function PlanManagementPage() {
  const {
    savedPlans,
    folders,
    selectedPlanIds,
    viewMode,
    sortBy,
    sortOrder,
    filterBy,
    searchQuery,
    getFilteredPlans,
    getFavoritePlans,
    getRecentPlans,
    getStatistics,
    getAllTags,
    getAllDestinations,
    setViewMode,
    setSorting,
    setFilter,
    setSearchQuery,
    clearFilters,
    selectPlan,
    deselectPlan,
    selectAllPlans,
    deselectAllPlans,
    toggleFavorite,
    deletePlan,
    duplicatePlan,
    markAsViewed
  } = usePlanManagementStore()

  const { addNotification } = useNotificationStore()
  const [showFilters, setShowFilters] = useState(false)
  
  const filteredPlans = getFilteredPlans()
  const statistics = getStatistics()
  const allTags = getAllTags()
  const allDestinations = getAllDestinations()

  const handlePlanClick = (planId: string) => {
    markAsViewed(planId)
    window.location.href = `/my-plans/${planId}`
  }

  const handleToggleFavorite = (planId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    toggleFavorite(planId)
    
    const plan = savedPlans.find(p => p.id === planId)
    if (plan) {
      addNotification({
        type: 'success',
        title: plan.is_favorite ? 'Removed from Favorites' : 'Added to Favorites',
        message: `${plan.name} ${plan.is_favorite ? 'removed from' : 'added to'} your favorites.`,
        duration: 3000
      })
    }
  }

  const handleDeletePlan = (planId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const plan = savedPlans.find(p => p.id === planId)
    if (plan && window.confirm(`Are you sure you want to delete "${plan.name}"?`)) {
      deletePlan(planId)
      addNotification({
        type: 'success',
        title: 'Plan Deleted',
        message: `${plan.name} has been deleted.`,
        duration: 3000
      })
    }
  }

  const handleDuplicatePlan = (planId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const newId = duplicatePlan(planId)
    const originalPlan = savedPlans.find(p => p.id === planId)
    
    if (originalPlan) {
      addNotification({
        type: 'success',
        title: 'Plan Duplicated',
        message: `Created a copy of "${originalPlan.name}".`,
        duration: 3000
      })
    }
  }

  const handleBulkAction = (action: 'delete' | 'favorite' | 'unfavorite') => {
    if (selectedPlanIds.length === 0) return

    switch (action) {
      case 'delete':
        if (window.confirm(`Are you sure you want to delete ${selectedPlanIds.length} selected plans?`)) {
          selectedPlanIds.forEach(deletePlan)
          deselectAllPlans()
          addNotification({
            type: 'success',
            title: 'Plans Deleted',
            message: `${selectedPlanIds.length} plans have been deleted.`,
            duration: 3000
          })
        }
        break
      case 'favorite':
        selectedPlanIds.forEach(id => {
          const plan = savedPlans.find(p => p.id === id)
          if (plan && !plan.is_favorite) toggleFavorite(id)
        })
        deselectAllPlans()
        addNotification({
          type: 'success',
          title: 'Plans Favorited',
          message: `Selected plans added to favorites.`,
          duration: 3000
        })
        break
      case 'unfavorite':
        selectedPlanIds.forEach(id => {
          const plan = savedPlans.find(p => p.id === id)
          if (plan && plan.is_favorite) toggleFavorite(id)
        })
        deselectAllPlans()
        addNotification({
          type: 'success',
          title: 'Plans Unfavorited',
          message: `Selected plans removed from favorites.`,
          duration: 3000
        })
        break
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">
                📋 My Travel Plans
              </h1>
              
              {selectedPlanIds.length > 0 && (
                <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
                  <span className="text-sm font-medium text-blue-700">
                    {selectedPlanIds.length} selected
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleBulkAction('favorite')}
                    className="h-7 px-2"
                  >
                    <Heart className="w-3 h-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleBulkAction('delete')}
                    className="h-7 px-2 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={deselectAllPlans}
                    className="h-7 px-2"
                  >
                    Clear
                  </Button>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Link href="/trip-generation">
                <Button className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  New Trip
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Plans:</span>
                  <span className="font-medium">{statistics.total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Favorites:</span>
                  <span className="font-medium">{statistics.favorites}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Folders:</span>
                  <span className="font-medium">{statistics.folders}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tags:</span>
                  <span className="font-medium">{statistics.tags}</span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Filters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setFilter({ favorites: true })}
                >
                  <Heart className="w-4 h-4 mr-2" />
                  Favorites ({statistics.favorites})
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setFilter({ favorites: false })}
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Recent ({statistics.recentlyViewed})
                </Button>
                {filterBy.favorites || filterBy.tags.length > 0 || filterBy.destinations.length > 0 ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={clearFilters}
                  >
                    Clear Filters
                  </Button>
                ) : null}
              </CardContent>
            </Card>

            {/* Popular Tags */}
            {allTags.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Tags</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1">
                    {allTags.slice(0, 10).map(tag => (
                      <Badge
                        key={tag}
                        variant={filterBy.tags.includes(tag) ? "default" : "secondary"}
                        className="cursor-pointer text-xs"
                        onClick={() => {
                          if (filterBy.tags.includes(tag)) {
                            setFilter({ tags: filterBy.tags.filter(t => t !== tag) })
                          } else {
                            setFilter({ tags: [...filterBy.tags, tag] })
                          }
                        }}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Folders */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Folders</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <FolderManager 
                  onFolderSelect={(folderId) => {
                    // Filter plans by folder
                    setFilter({ folder: folderId })
                  }}
                  selectedFolderId={filterBy.folder}
                />
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              {/* Search */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search plans..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* View Controls */}
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="w-4 h-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                >
                  <List className="w-4 h-4" />
                </Button>

                {/* Sort */}
                <select
                  className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                  value={`${sortBy}-${sortOrder}`}
                  onChange={(e) => {
                    const [newSortBy, newSortOrder] = e.target.value.split('-') as [typeof sortBy, typeof sortOrder]
                    setSorting(newSortBy, newSortOrder)
                  }}
                >
                  <option value="date_saved-desc">Newest First</option>
                  <option value="date_saved-asc">Oldest First</option>
                  <option value="name-asc">Name A-Z</option>
                  <option value="name-desc">Name Z-A</option>
                  <option value="destination-asc">Destination A-Z</option>
                  <option value="last_viewed-desc">Recently Viewed</option>
                </select>

                {selectedPlanIds.length === 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={selectAllPlans}
                  >
                    Select All
                  </Button>
                )}
              </div>
            </div>

            {/* Plans Grid/List */}
            {filteredPlans.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <Calendar className="w-16 h-16 mx-auto mb-4" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No travel plans found</h3>
                  <p className="text-gray-600 mb-4">
                    {savedPlans.length === 0 
                      ? "Start planning your first trip!" 
                      : "Try adjusting your search or filters."}
                  </p>
                  <Link href="/trip-generation">
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      Create Your First Trip
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <div className={cn(
                viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6' 
                  : 'space-y-4'
              )}>
                {filteredPlans.map(plan => (
                  <PlanCard
                    key={plan.id}
                    plan={plan}
                    isSelected={selectedPlanIds.includes(plan.id)}
                    viewMode={viewMode}
                    onSelect={() => selectPlan(plan.id)}
                    onDeselect={() => deselectPlan(plan.id)}
                    onToggleFavorite={handleToggleFavorite}
                    onDelete={handleDeletePlan}
                    onDuplicate={handleDuplicatePlan}
                    onClick={handlePlanClick}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

// Plan Card Component
interface PlanCardProps {
  plan: any
  isSelected: boolean
  viewMode: 'grid' | 'list'
  onSelect: () => void
  onDeselect: () => void
  onToggleFavorite: (planId: string, e: React.MouseEvent) => void
  onDelete: (planId: string, e: React.MouseEvent) => void
  onDuplicate: (planId: string, e: React.MouseEvent) => void
  onClick: (planId: string) => void
}

function PlanCard({
  plan,
  isSelected,
  viewMode,
  onSelect,
  onDeselect,
  onToggleFavorite,
  onDelete,
  onDuplicate,
  onClick
}: PlanCardProps) {
  const handleSelect = (e: React.ChangeEvent<HTMLInputElement> | React.MouseEvent) => {
    e.stopPropagation()
    if (isSelected) {
      onDeselect()
    } else {
      onSelect()
    }
  }

  if (viewMode === 'list') {
    return (
      <Card 
        className={cn(
          "cursor-pointer hover:shadow-md transition-all duration-200",
          isSelected && "ring-2 ring-blue-500 bg-blue-50"
        )}
        onClick={() => onClick(plan.id)}
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={handleSelect}
                className="w-4 h-4 rounded border-gray-300"
              />
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium text-gray-900">{plan.name}</h3>
                  {plan.is_favorite && (
                    <Heart className="w-4 h-4 text-red-500 fill-current" />
                  )}
                </div>
                
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {plan.destination}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {plan.duration_days} days
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(plan.start_date).toLocaleDateString()}
                  </div>
                  {plan.view_count > 0 && (
                    <div className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {plan.view_count}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => onToggleFavorite(plan.id, e)}
              >
                <Heart className={cn(
                  "w-4 h-4",
                  plan.is_favorite ? "text-red-500 fill-current" : "text-gray-400"
                )} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => onDuplicate(plan.id, e)}
              >
                <Copy className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => onDelete(plan.id, e)}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Grid view
  return (
    <Card 
      className={cn(
        "cursor-pointer hover:shadow-lg transition-all duration-200",
        isSelected && "ring-2 ring-blue-500 bg-blue-50"
      )}
      onClick={() => onClick(plan.id)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-2 flex-1">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={handleSelect}
              className="w-4 h-4 rounded border-gray-300 mt-1"
            />
            <div className="flex-1">
              <CardTitle className="text-lg line-clamp-1">{plan.name}</CardTitle>
              <CardDescription className="flex items-center gap-1 mt-1">
                <MapPin className="w-3 h-3" />
                {plan.destination}
              </CardDescription>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => onToggleFavorite(plan.id, e)}
            className="p-1 h-6 w-6"
          >
            <Heart className={cn(
              "w-4 h-4",
              plan.is_favorite ? "text-red-500 fill-current" : "text-gray-400"
            )} />
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(plan.start_date).toLocaleDateString()}
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {plan.duration_days} days
            </div>
          </div>

          {plan.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {plan.tags.slice(0, 3).map((tag: string) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {plan.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{plan.tags.length - 3}
                </Badge>
              )}
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="text-xs text-gray-500">
              {plan.view_count > 0 ? `Viewed ${plan.view_count} times` : 'Not viewed yet'}
            </div>
            
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => onDuplicate(plan.id, e)}
                className="p-1 h-6 w-6"
              >
                <Copy className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => onDelete(plan.id, e)}
                className="p-1 h-6 w-6 text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
