/**
 * useAdminAPIManager Hook
 * 
 * React hook to provide AdminAPIManager instance to components.
 */

import { useMemo } from 'react';
import { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

export function useAdminAPIManager(): AdminAPIManager {
  return useMemo(() => new AdminAPIManager(), []);
}
