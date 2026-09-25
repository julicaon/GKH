import { Link, useLocation, useSearchParams } from 'react-router-dom';
import type { ReactNode } from 'react';
import { useBridge } from '../shared/bridge/useBridge';

type DevRole = 'resident' | 'dispatcher';

function parseRole(value: string | null): DevRole {
  return value === 'dispatcher' ? 'dispatcher' : 'resident';
}

export function DevShell({ children }: { children: ReactNode }) {
  const [params] = useSearchParams();
  const location = useLocation();
  const { user } = useBridge();

  const role = parseRole(params.get('devRole'));
  const userId = params.get('devUserId') || user?.userId || 'dev-resident-1';

  const withRole = (nextRole: DevRole) => {
    const sp = new URLSearchParams(params);
    sp.set('devRole', nextRole);
    if (!sp.get('devUserId')) sp.set('devUserId', userId);
    return `${location.pathname}?${sp.toString()}`;
  };

  const colorScheme = params.get('colorScheme') === 'dark' ? 'dark' : 'light';
  const platform = params.get('platform') === 'ios' ? 'ios' : 'android';

  return (
    <div data-dev-color-scheme={colorScheme} data-dev-platform={platform}>
      <div className="devshell-banner">
        <span>
          DevShell | role={role} | userId={userId}
        </span>
        <span className="row">
          <Link to={withRole('resident')}>resident</Link>
          <Link to={`/dispatcher/login?${params.toString()}`}>dispatcher</Link>
          <Link to={`/dispatcher?devRole=dispatcher&devUserId=${encodeURIComponent(userId)}`}>
            feed
          </Link>
        </span>
      </div>
      {children}
    </div>
  );
}

export function useDevShellOverrides(): {
  platform: 'android' | 'ios';
  colorScheme: 'light' | 'dark';
  role: DevRole;
  userId: string;
} {
  const [params] = useSearchParams();
  const { user } = useBridge();
  return {
    platform: params.get('platform') === 'ios' ? 'ios' : 'android',
    colorScheme: params.get('colorScheme') === 'dark' ? 'dark' : 'light',
    role: parseRole(params.get('devRole')),
    userId: params.get('devUserId') || user?.userId || 'dev-resident-1',
  };
}
