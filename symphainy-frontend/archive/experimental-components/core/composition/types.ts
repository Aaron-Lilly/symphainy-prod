/**
 * Composition Types
 * Type definitions for component composition
 */

import React, { ReactNode } from 'react';

export interface CompositionConfig {
  enableContextComposition: boolean;
  enableRenderProps: boolean;
  enableCompoundComponents: boolean;
  enableHigherOrderComponents: boolean;
}

export interface RenderPropsConfig<T = any> {
  render: (props: T) => ReactNode;
  children?: (props: T) => ReactNode;
} 