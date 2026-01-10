/**
 * Enhanced Component Provider Context
 * Context setup and types for enhanced component functionality
 */

import React, { createContext } from 'react';
import { ComponentConfig } from '../AdvancedComponent';
import { LifecycleConfig } from '../lifecycle';
import { OptimizationConfig } from '../optimization';
import { CompositionConfig } from '../composition';

export interface EnhancedComponentContextValue {
  componentConfig: ComponentConfig;
  lifecycleConfig: LifecycleConfig;
  optimizationConfig: OptimizationConfig;
  compositionConfig: CompositionConfig;
  isEnabled: boolean;
}

export interface EnhancedComponentProviderProps {
  children: React.ReactNode;
  config?: {
    component?: Partial<ComponentConfig>;
    lifecycle?: Partial<LifecycleConfig>;
    optimization?: Partial<OptimizationConfig>;
    composition?: Partial<CompositionConfig>;
  };
}

export const EnhancedComponentContext = createContext<EnhancedComponentContextValue | null>(null); 