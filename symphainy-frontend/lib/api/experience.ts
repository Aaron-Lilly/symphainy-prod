/**
 * Experience API Module
 * 
 * Types and API functions for experience-related operations.
 */

export interface SourceFile {
  id: string;
  uuid?: string;
  filename: string;
  file_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  size?: number;
  created_at?: string;
  error?: string;
  [key: string]: any;
}

export interface ExperienceData {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  source_files?: SourceFile[];
}

export async function getExperience(id: string): Promise<{ success: boolean; experience?: ExperienceData; error?: string }> {
  console.warn('[experience API] getExperience - stub implementation');
  return { success: true, experience: { id, name: '', created_at: new Date().toISOString() } };
}

export async function listSourceFiles(): Promise<{ success: boolean; files: SourceFile[]; error?: string }> {
  console.warn('[experience API] listSourceFiles - stub implementation');
  return { success: true, files: [] };
}
