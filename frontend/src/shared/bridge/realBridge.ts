import type { MaxBridgePort, MaxBridgeUser } from './MaxBridgePort';

/**
 * Placeholder for real MAX WebApp bridge.
 * Falls back to mock identity until WebApp SDK is wired.
 */
export function createRealBridge(): MaxBridgePort {
  return {
    async getUser(): Promise<MaxBridgeUser> {
      const webApp = (
        window as unknown as {
          WebApp?: { initDataUnsafe?: { user?: { id?: number | string } } };
        }
      ).WebApp;
      const id = webApp?.initDataUnsafe?.user?.id;
      if (id != null) {
        return { userId: String(id), platform: 'android' };
      }
      return { userId: 'unknown-max-user', platform: 'android' };
    },
  };
}
