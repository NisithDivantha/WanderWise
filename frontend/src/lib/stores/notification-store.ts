import { create } from 'zustand'
import { NotificationState } from '@/types/api'

interface NotificationStore {
  notifications: NotificationState[]
  addNotification: (notification: Omit<NotificationState, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  clearAllNotifications: () => void
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],

  addNotification: (notificationData) => {
    const notification: NotificationState = {
      ...notificationData,
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
    }

    set((state) => ({
      notifications: [...state.notifications, notification]
    }))

    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        get().removeNotification(notification.id)
      }, notification.duration)
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter(n => n.id !== id)
    }))
  },

  clearAllNotifications: () => {
    set({ notifications: [] })
  }
}))
