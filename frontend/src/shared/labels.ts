import type { TicketStatus, UrgencyLevel } from './api/types';

export const STATUS_LABEL: Record<TicketStatus, string> = {
  NEW: 'Новая',
  ACCEPTED: 'Принята диспетчером',
  IN_PROGRESS: 'В работе у мастера',
  DONE: 'Выполнена',
  CANCELLED_BY_RESIDENT: 'Отменена жителем',
};

export const URGENCY_LABEL: Record<UrgencyLevel, string> = {
  HIGH: 'Срочная',
  MEDIUM: 'Средняя',
  LOW: 'Обычная',
};

export function statusLabel(status: TicketStatus): string {
  return STATUS_LABEL[status] ?? status;
}

export function urgencyLabel(level: UrgencyLevel): string {
  return URGENCY_LABEL[level] ?? level;
}

export function statusTone(status: TicketStatus): 'new' | 'progress' | 'done' | 'cancel' {
  switch (status) {
    case 'DONE':
      return 'done';
    case 'CANCELLED_BY_RESIDENT':
      return 'cancel';
    case 'IN_PROGRESS':
    case 'ACCEPTED':
      return 'progress';
    default:
      return 'new';
  }
}
