import { apiRequest } from './client';
import type { SubmitTicketBody, Ticket } from './types';

export function createTicket(body: SubmitTicketBody, maxUserId: string): Promise<Ticket> {
  return apiRequest<Ticket>('/api/tickets', {
    method: 'POST',
    body,
    maxUserId,
    auth: false,
  });
}

export function listTickets(
  role: 'resident' | 'org',
  opts?: { maxUserId?: string },
): Promise<Ticket[]> {
  return apiRequest<Ticket[]>('/api/tickets', {
    query: { role },
    maxUserId: opts?.maxUserId,
    auth: role === 'org',
  });
}

export function getTicket(id: string): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}`, { auth: false });
}

export function acceptTicket(id: string): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}/accept`, { method: 'POST' });
}

export function assignTicket(id: string, specialistId: string): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}/assign`, {
    method: 'POST',
    body: { specialistId },
  });
}

export function completeTicket(id: string): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}/complete`, { method: 'POST' });
}

export function cancelTicket(
  id: string,
  maxUserId: string,
  reason: string,
): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}/cancel`, {
    method: 'POST',
    body: { reason },
    maxUserId,
    auth: false,
  });
}
