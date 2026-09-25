import { apiRequest } from './client';
import type { Specialist, SpecialistCreate } from './types';

export function listSpecialists(opts?: {
  organizationId?: string;
  activeOnly?: boolean;
}): Promise<Specialist[]> {
  return apiRequest<Specialist[]>('/api/specialists', {
    query: {
      organizationId: opts?.organizationId,
      active_only: opts?.activeOnly ?? false,
    },
  });
}

export function createSpecialist(body: SpecialistCreate): Promise<Specialist> {
  return apiRequest<Specialist>('/api/specialists', { method: 'POST', body });
}
