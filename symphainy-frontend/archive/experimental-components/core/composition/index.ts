/**
 * Composition Orchestrator
 * Unified access point for composition functionality
 */

// Types
export type {
  CompositionConfig,
  RenderPropsConfig
} from './types';

// Pattern-based composition
export {
  useRenderProps,
  useCompoundComponent,
  createHOC,
  useComponentComposition,
  useComponentFactory,
  useConditionalComponent,
  useComponentPipeline
} from './patterns';

// Context-based composition
export {
  useContextComposition,
  createContextProvider,
  useComponentRegistry,
  createComposedComponent
} from './context'; 