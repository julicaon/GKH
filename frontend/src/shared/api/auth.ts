import { apiRequest, setStoredToken } from './client';
import type { LoginResponse } from './types';

const ORG_KEY = 'dispatcher_organization_id';
const DISPATCHER_KEY = 'dispatcher_id';
const USERNAME_KEY = 'dispatcher_username';

export async function login(username: string, password: string): Promise<LoginResponse> {
  const data = await apiRequest<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: { username, password },
    auth: false,
  });
  setStoredToken(data.access_token);
  localStorage.setItem(ORG_KEY, data.organization_id);
  localStorage.setItem(DISPATCHER_KEY, data.dispatcher_id);
  localStorage.setItem(USERNAME_KEY, data.username);
  return data;
}

export function logout(): void {
  setStoredToken(null);
  localStorage.removeItem(ORG_KEY);
  localStorage.removeItem(DISPATCHER_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

export function getDispatcherSession(): {
  organizationId: string | null;
  dispatcherId: string | null;
  username: string | null;
} {
  return {
    organizationId: localStorage.getItem(ORG_KEY),
    dispatcherId: localStorage.getItem(DISPATCHER_KEY),
    username: localStorage.getItem(USERNAME_KEY),
  };
}
