/**
 * Experience Dimension API
 * 
 * Stub implementation for experience dimension operations.
 */

export interface ExperienceDimension {
  id: string;
  name: string;
  value: number;
  description?: string;
}

export interface UserContext {
  user_id?: string;
  full_name?: string;
  email?: string;
  name?: string;
  preferences?: Record<string, any>;
  session_id?: string;
  permissions?: string[];
}

export interface UpdateDimensionResponse {
  success: boolean;
  dimension?: ExperienceDimension;
  error?: string;
}

export async function getDimensions(): Promise<{ success: boolean; dimensions: ExperienceDimension[]; error?: string }> {
  console.warn('[experience-dimension API] getDimensions - stub implementation');
  return { success: true, dimensions: [] };
}

export async function updateDimension(id: string, value: number): Promise<UpdateDimensionResponse> {
  console.warn('[experience-dimension API] updateDimension - stub implementation');
  return { success: true, dimension: { id, name: '', value } };
}

export async function createDimension(data: Partial<ExperienceDimension>): Promise<UpdateDimensionResponse> {
  console.warn('[experience-dimension API] createDimension - stub implementation');
  return { success: true, dimension: { id: '', name: '', value: 0, ...data } as ExperienceDimension };
}
