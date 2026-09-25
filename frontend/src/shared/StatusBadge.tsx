import type { TicketStatus, UrgencyLevel } from './api/types';
import { statusLabel, statusTone, urgencyLabel } from './labels';

type StatusBadgeProps = {
  status: TicketStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge--${statusTone(status)}`}>
      {statusLabel(status)}
    </span>
  );
}

type UrgencyBadgeProps = {
  level: UrgencyLevel;
};

export function UrgencyBadge({ level }: UrgencyBadgeProps) {
  return (
    <span className={`urgency-badge urgency-badge--${level.toLowerCase()}`}>
      {urgencyLabel(level)}
    </span>
  );
}
