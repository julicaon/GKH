export type MaxBridgeUser = {
  userId: string;
  platform: 'android' | 'ios' | 'web';
};

export interface MaxBridgePort {
  getUser(): Promise<MaxBridgeUser>;
}
