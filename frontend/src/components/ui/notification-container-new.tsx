'use client'

import React, { useEffect, useState } from 'react'
import { useNotifications } from '@/lib/stores/notifications'
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
}

const colorMap = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
}

const NotificationContainer: React.FC = () => {
  const [isClient, setIsClient] = useState(false)
  const { notifications, removeNotification } = useNotifications()

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient || notifications.length === 0) {
    return null
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => {
        const Icon = iconMap[notification.type]
        
        return (
          <div
            key={notification.id}
            className={`
              p-4 rounded-lg border shadow-lg animate-in slide-in-from-right-full
              ${colorMap[notification.type]}
            `}
          >
            <div className="flex items-start gap-3">
              <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-sm">
                  {notification.title}
                </h3>
                {notification.message && (
                  <p className="text-sm opacity-90 mt-1">
                    {notification.message}
                  </p>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 hover:bg-white/20"
                onClick={() => removeNotification(notification.id)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export { NotificationContainer }
