import { useEffect, useMemo, useState } from 'react';
import type { MaxBridgePort, MaxBridgeUser } from './MaxBridgePort';
import { createMockBridge } from './mockBridge';
import { createRealBridge } from './realBridge';

const MAX_MODE = (import.meta.env.VITE_MAX_MODE as string | undefined) ?? 'mock';

export function getBridge(): MaxBridgePort {
  return MAX_MODE === 'real' ? createRealBridge() : createMockBridge();
}

export function useBridge(): {
  user: MaxBridgeUser | null;
  loading: boolean;
  error: string | null;
} {
  const bridge = useMemo(() => getBridge(), []);
  const [user, setUser] = useState<MaxBridgeUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    bridge
      .getUser()
      .then((u) => {
        if (!cancelled) {
          setUser(u);
          setError(null);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка bridge');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [bridge]);

  return { user, loading, error };
}
