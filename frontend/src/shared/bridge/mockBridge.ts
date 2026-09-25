import type { MaxBridgePort, MaxBridgeUser } from './MaxBridgePort';

function readQueryUserId(): string | null {
  const params = new URLSearchParams(window.location.search);
  return params.get('devUserId');
}

export function createMockBridge(defaultUserId = 'dev-resident-1'): MaxBridgePort {
  return {
    async getUser(): Promise<MaxBridgeUser> {
      return {
        userId: readQueryUserId() || defaultUserId,
        platform: 'android',
      };
    },
  };
}
