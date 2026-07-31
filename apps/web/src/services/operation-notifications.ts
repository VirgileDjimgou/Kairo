export type OperationNotificationLevel = 'success' | 'error' | 'warning' | 'info'

export type OperationNotification = {
  level: OperationNotificationLevel
  messageKey: string
  detail?: string
}

const EVENT_NAME = 'kairo:operation-notification'

export function notifyOperation(notification: OperationNotification): void {
  window.dispatchEvent(new CustomEvent<OperationNotification>(EVENT_NAME, { detail: notification }))
}

export function listenForOperationNotifications(
  listener: (notification: OperationNotification) => void,
): () => void {
  const handler = (event: Event) => listener((event as CustomEvent<OperationNotification>).detail)
  window.addEventListener(EVENT_NAME, handler)
  return () => window.removeEventListener(EVENT_NAME, handler)
}
