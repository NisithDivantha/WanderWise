import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { TravelPlan } from '@/types/api'

export interface SavedTravelPlan extends Omit<TravelPlan, 'plan_id'> {
  id: string
  name: string
  saved_at: string
  is_favorite: boolean
  tags: string[]
  notes?: string
  last_viewed?: string
  view_count: number
  duration_days: number // Make this required for saved plans
}

export interface PlanFolder {
  id: string
  name: string
  description?: string
  created_at: string
  plan_ids: string[]
  color?: string
}

interface PlanManagementState {
  // Saved plans
  savedPlans: SavedTravelPlan[]
  folders: PlanFolder[]
  
  // UI state
  selectedPlanIds: string[]
  viewMode: 'grid' | 'list'
  sortBy: 'name' | 'date_saved' | 'destination' | 'duration' | 'last_viewed'
  sortOrder: 'asc' | 'desc'
  filterBy: {
    tags: string[]
    destinations: string[]
    favorites: boolean
    folder?: string
  }
  searchQuery: string

  // Actions - Plan Management
  savePlan: (plan: TravelPlan, name?: string) => string
  deletePlan: (planId: string) => void
  updatePlan: (planId: string, updates: Partial<SavedTravelPlan>) => void
  duplicatePlan: (planId: string) => string
  toggleFavorite: (planId: string) => void
  addPlanTags: (planId: string, tags: string[]) => void
  removePlanTags: (planId: string, tags: string[]) => void
  updatePlanNotes: (planId: string, notes: string) => void
  markAsViewed: (planId: string) => void

  // Actions - Folder Management
  createFolder: (name: string, description?: string, color?: string) => string
  deleteFolder: (folderId: string) => void
  updateFolder: (folderId: string, updates: Partial<Omit<PlanFolder, 'id'>>) => void
  addPlansToFolder: (folderId: string, planIds: string[]) => void
  removePlansFromFolder: (folderId: string, planIds: string[]) => void

  // Actions - Selection & Bulk Operations
  selectPlan: (planId: string) => void
  deselectPlan: (planId: string) => void
  selectAllPlans: () => void
  deselectAllPlans: () => void
  bulkDelete: () => void
  bulkAddToFolder: (folderId: string) => void
  bulkToggleFavorite: () => void

  // Actions - View & Filter
  setViewMode: (mode: 'grid' | 'list') => void
  setSorting: (sortBy: PlanManagementState['sortBy'], order: 'asc' | 'desc') => void
  setFilter: (filter: Partial<PlanManagementState['filterBy']>) => void
  setSearchQuery: (query: string) => void
  clearFilters: () => void

  // Getters
  getFilteredPlans: () => SavedTravelPlan[]
  getPlansByFolder: (folderId: string) => SavedTravelPlan[]
  getFavoritePlans: () => SavedTravelPlan[]
  getRecentPlans: (limit?: number) => SavedTravelPlan[]
  getAllTags: () => string[]
  getAllDestinations: () => string[]
  getStatistics: () => {
    total: number
    favorites: number
    folders: number
    tags: number
    recentlyViewed: number
  }
}

export const usePlanManagementStore = create<PlanManagementState>()(
  persist(
    (set, get) => ({
      // Initial state
      savedPlans: [],
      folders: [],
      selectedPlanIds: [],
      viewMode: 'grid',
      sortBy: 'date_saved',
      sortOrder: 'desc',
      filterBy: {
        tags: [],
        destinations: [],
        favorites: false
      },
      searchQuery: '',

      // Plan Management Actions
      savePlan: (plan, name) => {
        const id = `plan-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        
        // Calculate duration if not provided
        const duration = plan.duration_days || Math.ceil(
          (new Date(plan.end_date).getTime() - new Date(plan.start_date).getTime()) / (1000 * 60 * 60 * 24)
        )
        
        const savedPlan: SavedTravelPlan = {
          ...plan,
          id,
          name: name || `${plan.destination} Trip`,
          saved_at: new Date().toISOString(),
          is_favorite: false,
          tags: [],
          view_count: 0,
          duration_days: duration
        }

        set((state) => ({
          savedPlans: [savedPlan, ...state.savedPlans]
        }))

        return id
      },

      deletePlan: (planId) => {
        set((state) => ({
          savedPlans: state.savedPlans.filter(p => p.id !== planId),
          selectedPlanIds: state.selectedPlanIds.filter(id => id !== planId),
          folders: state.folders.map(folder => ({
            ...folder,
            plan_ids: folder.plan_ids.filter(id => id !== planId)
          }))
        }))
      },

      updatePlan: (planId, updates) => {
        set((state) => ({
          savedPlans: state.savedPlans.map(plan =>
            plan.id === planId ? { ...plan, ...updates } : plan
          )
        }))
      },

      duplicatePlan: (planId) => {
        const originalPlan = get().savedPlans.find(p => p.id === planId)
        if (!originalPlan) return ''

        const newId = `plan-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        const duplicatedPlan: SavedTravelPlan = {
          ...originalPlan,
          id: newId,
          name: `${originalPlan.name} (Copy)`,
          saved_at: new Date().toISOString(),
          view_count: 0,
          duration_days: originalPlan.duration_days
        }

        set((state) => ({
          savedPlans: [duplicatedPlan, ...state.savedPlans]
        }))

        return newId
      },

      toggleFavorite: (planId) => {
        set((state) => ({
          savedPlans: state.savedPlans.map(plan =>
            plan.id === planId ? { ...plan, is_favorite: !plan.is_favorite } : plan
          )
        }))
      },

      addPlanTags: (planId, tags) => {
        set((state) => ({
          savedPlans: state.savedPlans.map(plan =>
            plan.id === planId 
              ? { ...plan, tags: [...new Set([...plan.tags, ...tags])] }
              : plan
          )
        }))
      },

      removePlanTags: (planId, tags) => {
        set((state) => ({
          savedPlans: state.savedPlans.map(plan =>
            plan.id === planId 
              ? { ...plan, tags: plan.tags.filter(tag => !tags.includes(tag)) }
              : plan
          )
        }))
      },

      updatePlanNotes: (planId, notes) => {
        get().updatePlan(planId, { notes })
      },

      markAsViewed: (planId) => {
        set((state) => ({
          savedPlans: state.savedPlans.map(plan =>
            plan.id === planId 
              ? { 
                  ...plan, 
                  last_viewed: new Date().toISOString(),
                  view_count: plan.view_count + 1
                }
              : plan
          )
        }))
      },

      // Folder Management Actions
      createFolder: (name, description, color) => {
        const id = `folder-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        const folder: PlanFolder = {
          id,
          name,
          description,
          color: color || '#3B82F6',
          created_at: new Date().toISOString(),
          plan_ids: []
        }

        set((state) => ({
          folders: [...state.folders, folder]
        }))

        return id
      },

      deleteFolder: (folderId) => {
        set((state) => ({
          folders: state.folders.filter(f => f.id !== folderId)
        }))
      },

      updateFolder: (folderId, updates) => {
        set((state) => ({
          folders: state.folders.map(folder =>
            folder.id === folderId ? { ...folder, ...updates } : folder
          )
        }))
      },

      addPlansToFolder: (folderId, planIds) => {
        set((state) => ({
          folders: state.folders.map(folder =>
            folder.id === folderId 
              ? { ...folder, plan_ids: [...new Set([...folder.plan_ids, ...planIds])] }
              : folder
          )
        }))
      },

      removePlansFromFolder: (folderId, planIds) => {
        set((state) => ({
          folders: state.folders.map(folder =>
            folder.id === folderId 
              ? { ...folder, plan_ids: folder.plan_ids.filter(id => !planIds.includes(id)) }
              : folder
          )
        }))
      },

      // Selection & Bulk Operations
      selectPlan: (planId) => {
        set((state) => ({
          selectedPlanIds: [...new Set([...state.selectedPlanIds, planId])]
        }))
      },

      deselectPlan: (planId) => {
        set((state) => ({
          selectedPlanIds: state.selectedPlanIds.filter(id => id !== planId)
        }))
      },

      selectAllPlans: () => {
        const filteredPlans = get().getFilteredPlans()
        set({
          selectedPlanIds: filteredPlans.map(p => p.id)
        })
      },

      deselectAllPlans: () => {
        set({ selectedPlanIds: [] })
      },

      bulkDelete: () => {
        const { selectedPlanIds } = get()
        selectedPlanIds.forEach(planId => get().deletePlan(planId))
        set({ selectedPlanIds: [] })
      },

      bulkAddToFolder: (folderId) => {
        const { selectedPlanIds } = get()
        get().addPlansToFolder(folderId, selectedPlanIds)
        set({ selectedPlanIds: [] })
      },

      bulkToggleFavorite: () => {
        const { selectedPlanIds, savedPlans } = get()
        const hasUnfavorited = selectedPlanIds.some(id => {
          const plan = savedPlans.find(p => p.id === id)
          return plan && !plan.is_favorite
        })

        selectedPlanIds.forEach(planId => {
          const plan = savedPlans.find(p => p.id === planId)
          if (plan) {
            get().updatePlan(planId, { is_favorite: hasUnfavorited })
          }
        })
        set({ selectedPlanIds: [] })
      },

      // View & Filter Actions
      setViewMode: (mode) => {
        set({ viewMode: mode })
      },

      setSorting: (sortBy, order) => {
        set({ sortBy, sortOrder: order })
      },

      setFilter: (filter) => {
        set((state) => ({
          filterBy: { ...state.filterBy, ...filter }
        }))
      },

      setSearchQuery: (query) => {
        set({ searchQuery: query })
      },

      clearFilters: () => {
        set({
          filterBy: {
            tags: [],
            destinations: [],
            favorites: false
          },
          searchQuery: ''
        })
      },

      // Getters
      getFilteredPlans: () => {
        const { savedPlans, filterBy, searchQuery, sortBy, sortOrder } = get()
        
        let filtered = [...savedPlans]

        // Apply search
        if (searchQuery) {
          const query = searchQuery.toLowerCase()
          filtered = filtered.filter(plan =>
            plan.name.toLowerCase().includes(query) ||
            plan.destination.toLowerCase().includes(query) ||
            plan.tags.some(tag => tag.toLowerCase().includes(query)) ||
            plan.notes?.toLowerCase().includes(query)
          )
        }

        // Apply filters
        if (filterBy.favorites) {
          filtered = filtered.filter(plan => plan.is_favorite)
        }

        if (filterBy.tags.length > 0) {
          filtered = filtered.filter(plan =>
            filterBy.tags.some(tag => plan.tags.includes(tag))
          )
        }

        if (filterBy.destinations.length > 0) {
          filtered = filtered.filter(plan =>
            filterBy.destinations.includes(plan.destination)
          )
        }

        if (filterBy.folder) {
          const folder = get().folders.find(f => f.id === filterBy.folder)
          if (folder) {
            filtered = filtered.filter(plan => folder.plan_ids.includes(plan.id))
          }
        }

        // Apply sorting
        filtered.sort((a, b) => {
          let compareValue = 0

          switch (sortBy) {
            case 'name':
              compareValue = a.name.localeCompare(b.name)
              break
            case 'date_saved':
              compareValue = new Date(a.saved_at).getTime() - new Date(b.saved_at).getTime()
              break
            case 'destination':
              compareValue = a.destination.localeCompare(b.destination)
              break
            case 'duration':
              compareValue = (a.duration_days || 0) - (b.duration_days || 0)
              break
            case 'last_viewed':
              const aViewed = a.last_viewed ? new Date(a.last_viewed).getTime() : 0
              const bViewed = b.last_viewed ? new Date(b.last_viewed).getTime() : 0
              compareValue = aViewed - bViewed
              break
          }

          return sortOrder === 'asc' ? compareValue : -compareValue
        })

        return filtered
      },

      getPlansByFolder: (folderId) => {
        const { savedPlans, folders } = get()
        const folder = folders.find(f => f.id === folderId)
        if (!folder) return []

        return savedPlans.filter(plan => folder.plan_ids.includes(plan.id))
      },

      getFavoritePlans: () => {
        return get().savedPlans.filter(plan => plan.is_favorite)
      },

      getRecentPlans: (limit = 5) => {
        return get().savedPlans
          .sort((a, b) => new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime())
          .slice(0, limit)
      },

      getAllTags: () => {
        const allTags = get().savedPlans.flatMap(plan => plan.tags)
        return [...new Set(allTags)].sort()
      },

      getAllDestinations: () => {
        const destinations = get().savedPlans.map(plan => plan.destination)
        return [...new Set(destinations)].sort()
      },

      getStatistics: () => {
        const { savedPlans, folders } = get()
        const now = new Date()
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

        return {
          total: savedPlans.length,
          favorites: savedPlans.filter(p => p.is_favorite).length,
          folders: folders.length,
          tags: get().getAllTags().length,
          recentlyViewed: savedPlans.filter(p => 
            p.last_viewed && new Date(p.last_viewed) > oneWeekAgo
          ).length
        }
      }
    }),
    {
      name: 'plan-management-storage',
      version: 1
    }
  )
)
