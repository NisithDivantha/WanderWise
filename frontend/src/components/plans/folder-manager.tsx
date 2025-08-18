'use client'

import { useState } from 'react'
import { usePlanManagementStore } from '../../lib/stores/plan-management-store'
import { useNotificationStore } from '../../lib/stores/notification-store'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Plus, 
  Folder, 
  Edit, 
  Trash2, 
  Save, 
  X,
  FolderOpen,
  MoreVertical
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface FolderManagerProps {
  onFolderSelect?: (folderId: string) => void
  selectedFolderId?: string
}

export function FolderManager({ onFolderSelect, selectedFolderId }: FolderManagerProps) {
  const {
    folders,
    savedPlans,
    createFolder,
    deleteFolder,
    updateFolder,
    getPlansByFolder
  } = usePlanManagementStore()

  const { addNotification } = useNotificationStore()
  
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingFolder, setEditingFolder] = useState<string | null>(null)
  const [newFolderName, setNewFolderName] = useState('')
  const [newFolderDescription, setNewFolderDescription] = useState('')
  const [newFolderColor, setNewFolderColor] = useState('#3B82F6')

  const colors = [
    { name: 'Blue', value: '#3B82F6' },
    { name: 'Green', value: '#10B981' },
    { name: 'Purple', value: '#8B5CF6' },
    { name: 'Red', value: '#EF4444' },
    { name: 'Orange', value: '#F59E0B' },
    { name: 'Pink', value: '#EC4899' },
    { name: 'Indigo', value: '#6366F1' },
    { name: 'Teal', value: '#14B8A6' }
  ]

  const handleCreateFolder = () => {
    if (newFolderName.trim()) {
      const folderId = createFolder(newFolderName.trim(), newFolderDescription.trim() || undefined, newFolderColor)
      
      setNewFolderName('')
      setNewFolderDescription('')
      setNewFolderColor('#3B82F6')
      setShowCreateForm(false)
      
      addNotification({
        type: 'success',
        title: 'Folder Created',
        message: `Created folder "${newFolderName.trim()}".`,
        duration: 3000
      })
    }
  }

  const handleDeleteFolder = (folderId: string) => {
    const folder = folders.find(f => f.id === folderId)
    if (folder && window.confirm(`Are you sure you want to delete the folder &ldquo;${folder.name}&rdquo;? Plans inside will not be deleted.`)) {
      deleteFolder(folderId)
      addNotification({
        type: 'success',
        title: 'Folder Deleted',
        message: `Deleted folder "${folder.name}".`,
        duration: 3000
      })
    }
  }

  const handleUpdateFolder = (folderId: string, updates: any) => {
    updateFolder(folderId, updates)
    setEditingFolder(null)
    addNotification({
      type: 'success',
      title: 'Folder Updated',
      message: 'Folder has been updated.',
      duration: 3000
    })
  }

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Folders</h3>
        <Button
          size="sm"
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-1"
        >
          <Plus className="w-4 h-4" />
          New Folder
        </Button>
      </div>

      {/* Create Folder Form */}
      {showCreateForm && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div>
              <Input
                placeholder="Folder name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
              />
            </div>
            
            <div>
              <Input
                placeholder="Description (optional)"
                value={newFolderDescription}
                onChange={(e) => setNewFolderDescription(e.target.value)}
              />
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Color</p>
              <div className="flex gap-2">
                {colors.map(color => (
                  <button
                    key={color.value}
                    className={cn(
                      "w-6 h-6 rounded-full border-2 border-gray-200",
                      newFolderColor === color.value && "ring-2 ring-gray-400"
                    )}
                    style={{ backgroundColor: color.value }}
                    onClick={() => setNewFolderColor(color.value)}
                    title={color.name}
                  />
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleCreateFolder}
                disabled={!newFolderName.trim()}
              >
                Create
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false)
                  setNewFolderName('')
                  setNewFolderDescription('')
                  setNewFolderColor('#3B82F6')
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Folders List */}
      <div className="space-y-2">
        {folders.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Folder className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No folders yet</p>
              <p className="text-sm text-gray-400">Create folders to organize your travel plans</p>
            </CardContent>
          </Card>
        ) : (
          folders.map(folder => (
            <FolderCard
              key={folder.id}
              folder={folder}
              planCount={getPlansByFolder(folder.id).length}
              isSelected={selectedFolderId === folder.id}
              isEditing={editingFolder === folder.id}
              onSelect={() => onFolderSelect?.(folder.id)}
              onEdit={() => setEditingFolder(folder.id)}
              onCancelEdit={() => setEditingFolder(null)}
              onSave={handleUpdateFolder}
              onDelete={handleDeleteFolder}
            />
          ))
        )}
      </div>
    </div>
  )
}

// Folder Card Component
interface FolderCardProps {
  folder: any
  planCount: number
  isSelected: boolean
  isEditing: boolean
  onSelect: () => void
  onEdit: () => void
  onCancelEdit: () => void
  onSave: (folderId: string, updates: any) => void
  onDelete: (folderId: string) => void
}

function FolderCard({
  folder,
  planCount,
  isSelected,
  isEditing,
  onSelect,
  onEdit,
  onCancelEdit,
  onSave,
  onDelete
}: FolderCardProps) {
  const [editName, setEditName] = useState(folder.name)
  const [editDescription, setEditDescription] = useState(folder.description || '')
  const [editColor, setEditColor] = useState(folder.color || '#3B82F6')

  const colors = [
    { name: 'Blue', value: '#3B82F6' },
    { name: 'Green', value: '#10B981' },
    { name: 'Purple', value: '#8B5CF6' },
    { name: 'Red', value: '#EF4444' },
    { name: 'Orange', value: '#F59E0B' },
    { name: 'Pink', value: '#EC4899' },
    { name: 'Indigo', value: '#6366F1' },
    { name: 'Teal', value: '#14B8A6' }
  ]

  const handleSave = () => {
    onSave(folder.id, {
      name: editName,
      description: editDescription || undefined,
      color: editColor
    })
  }

  const handleCancel = () => {
    setEditName(folder.name)
    setEditDescription(folder.description || '')
    setEditColor(folder.color || '#3B82F6')
    onCancelEdit()
  }

  if (isEditing) {
    return (
      <Card>
        <CardContent className="pt-6 space-y-4">
          <Input
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
          />
          <Input
            placeholder="Description (optional)"
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
          />
          
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Color</p>
            <div className="flex gap-2">
              {colors.map(color => (
                <button
                  key={color.value}
                  className={cn(
                    "w-6 h-6 rounded-full border-2 border-gray-200",
                    editColor === color.value && "ring-2 ring-gray-400"
                  )}
                  style={{ backgroundColor: color.value }}
                  onClick={() => setEditColor(color.value)}
                  title={color.name}
                />
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            <Button size="sm" onClick={handleSave}>
              <Save className="w-4 h-4 mr-1" />
              Save
            </Button>
            <Button size="sm" variant="outline" onClick={handleCancel}>
              <X className="w-4 h-4 mr-1" />
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card 
      className={cn(
        "cursor-pointer hover:shadow-md transition-all duration-200",
        isSelected && "ring-2 ring-blue-500 bg-blue-50"
      )}
      onClick={onSelect}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: folder.color || '#3B82F6' }}
            />
            <div>
              <h4 className="font-medium text-gray-900">{folder.name}</h4>
              {folder.description && (
                <p className="text-sm text-gray-600">{folder.description}</p>
              )}
              <p className="text-xs text-gray-500">{planCount} plans</p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onEdit()
              }}
            >
              <Edit className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(folder.id)
              }}
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
