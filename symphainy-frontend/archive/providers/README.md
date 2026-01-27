# Archived Providers

This directory contains providers that have been archived as part of Phase 1: Provider Consolidation.

## Archived Files

### From `shared/agui/`
- `AuthProvider.tsx.archived` → Replaced by `shared/auth/AuthProvider.tsx`
- `AppProviders.tsx.archived` → Replaced by `shared/state/AppProviders.tsx`
- `SessionProvider.tsx.archived` → Replaced by `shared/state/SessionBoundaryProvider.tsx`
- `GlobalSessionProvider.tsx.archived` → Replaced by `shared/state/SessionBoundaryProvider.tsx`

### From `shared/session/`
- `GlobalSessionProvider.tsx.archived` → Replaced by `shared/state/SessionBoundaryProvider.tsx`

### From `shared/components/`
- `SessionProvider.tsx.archived` → Replaced by `shared/state/SessionBoundaryProvider.tsx`

## Migration Guide

If you need to reference these files:

1. **AuthProvider**: Use `shared/auth/AuthProvider.tsx`
2. **AppProviders**: Use `shared/state/AppProviders.tsx`
3. **Session Providers**: Use `shared/state/SessionBoundaryProvider.tsx`

## Date Archived
January 22, 2026

## Reason
Phase 1: Provider Consolidation - Eliminating duplicate providers to establish single source of truth.
