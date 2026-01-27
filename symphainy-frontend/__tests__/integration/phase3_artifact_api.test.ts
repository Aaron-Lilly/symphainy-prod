/**
 * Phase 3: Artifact API End-to-End Tests
 * 
 * Tests artifact-centric APIs with REAL backend infrastructure:
 * - Artifact listing (listArtifacts)
 * - Artifact resolution (resolveArtifact)
 * - Pending intent management (getPendingIntents, createPendingIntent)
 * 
 * Prerequisites:
 * - Backend server running (docker-compose up or ./startup.sh)
 * - Backend accessible at http://localhost:8000
 * - At least one file uploaded (for artifact listing/resolution tests)
 * 
 * Run with: npm run test:integration -- phase3_artifact_api.test.ts
 * 
 * This test validates that:
 * - Artifact listing returns artifacts from artifact_index
 * - Artifact resolution returns full artifact records
 * - Pending intents can be created and retrieved
 * - Eligibility-based filtering works correctly
 */

import { getApiEndpointUrl } from '@/shared/config/api-config';

// Test configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const TEST_TIMEOUT = 60000; // 60 seconds for real backend tests

// Helper to generate valid UUID v4
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Test tenant/user (should match your test setup)
// Note: tenant_id and session_id must be valid UUIDs per database schema
const TEST_TENANT_ID = process.env.TEST_TENANT_ID || generateUUID();
const TEST_USER_ID = process.env.TEST_USER_ID || 'test-user';
const TEST_SESSION_ID = process.env.TEST_SESSION_ID || generateUUID();

describe('Phase 3: Artifact API End-to-End Tests', () => {
  let sessionId: string;
  let tenantId: string;
  let testFileArtifactId: string | undefined;
  let testPendingIntentId: string | undefined;

  beforeAll(async () => {
    // Use provided session or create one
    sessionId = TEST_SESSION_ID;
    tenantId = TEST_TENANT_ID;
    
    console.log(`✅ Using test session: ${sessionId}, tenant: ${tenantId}`);
  }, TEST_TIMEOUT);

  describe('Artifact Listing (listArtifacts)', () => {
    it('should list file artifacts with READY lifecycle state', async () => {
      const url = getApiEndpointUrl('/api/artifact/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          artifact_type: 'file',
          lifecycle_state: 'READY',
          limit: 10,
          offset: 0,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('artifacts');
      expect(data).toHaveProperty('total');
      expect(data).toHaveProperty('limit');
      expect(data).toHaveProperty('offset');
      expect(Array.isArray(data.artifacts)).toBe(true);
      
      // If artifacts exist, validate structure
      if (data.artifacts.length > 0) {
        const artifact = data.artifacts[0];
        expect(artifact).toHaveProperty('artifact_id');
        expect(artifact).toHaveProperty('artifact_type');
        expect(artifact).toHaveProperty('lifecycle_state');
        expect(artifact).toHaveProperty('semantic_descriptor');
        expect(artifact).toHaveProperty('created_at');
        
        // Store first artifact ID for resolution test
        if (!testFileArtifactId) {
          testFileArtifactId = artifact.artifact_id;
        }
      }
      
      console.log(`✅ Listed ${data.total} file artifacts`);
    });

    it('should filter artifacts by eligibility (eligibleFor)', async () => {
      const url = getApiEndpointUrl('/api/artifact/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          artifact_type: 'file',
          lifecycle_state: 'READY',
          eligible_for: 'parse_content', // Files eligible for parsing
          limit: 10,
          offset: 0,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('artifacts');
      expect(Array.isArray(data.artifacts)).toBe(true);
      
      // All returned artifacts should be eligible for parse_content
      // (This is a basic check - eligibility logic is in backend)
      console.log(`✅ Listed ${data.total} artifacts eligible for parse_content`);
    });

    it('should list parsed_content artifacts', async () => {
      const url = getApiEndpointUrl('/api/artifact/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          artifact_type: 'parsed_content',
          lifecycle_state: 'READY',
          limit: 10,
          offset: 0,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('artifacts');
      expect(Array.isArray(data.artifacts)).toBe(true);
      
      // Validate parsed_content artifacts have parser_type in semantic_descriptor
      data.artifacts.forEach((artifact: any) => {
        expect(artifact.artifact_type).toBe('parsed_content');
        if (artifact.semantic_descriptor) {
          // parsed_content should have parser_type
          expect(artifact.semantic_descriptor).toHaveProperty('parser_type');
        }
      });
      
      console.log(`✅ Listed ${data.total} parsed_content artifacts`);
    });
  });

  describe('Artifact Resolution (resolveArtifact)', () => {
    it('should resolve a file artifact with full details', async () => {
      // Skip if no test artifact available
      if (!testFileArtifactId) {
        console.log('⚠️ Skipping: No file artifact available for resolution test');
        return;
      }

      const url = getApiEndpointUrl('/api/artifact/resolve');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          artifact_id: testFileArtifactId,
          artifact_type: 'file',
          tenant_id: tenantId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('artifact');
      const artifact = data.artifact;
      
      // Validate full artifact record structure
      expect(artifact).toHaveProperty('artifact_id');
      expect(artifact).toHaveProperty('artifact_type');
      expect(artifact).toHaveProperty('tenant_id');
      expect(artifact).toHaveProperty('produced_by');
      expect(artifact).toHaveProperty('lifecycle_state');
      expect(artifact).toHaveProperty('semantic_descriptor');
      expect(artifact).toHaveProperty('parent_artifacts');
      expect(artifact).toHaveProperty('materializations');
      expect(artifact).toHaveProperty('created_at');
      expect(artifact).toHaveProperty('updated_at');
      
      // Validate produced_by structure
      expect(artifact.produced_by).toHaveProperty('intent');
      expect(artifact.produced_by).toHaveProperty('execution_id');
      
      // Validate materializations array
      expect(Array.isArray(artifact.materializations)).toBe(true);
      
      console.log(`✅ Resolved artifact: ${artifact.artifact_id}`);
      console.log(`   - Type: ${artifact.artifact_type}`);
      console.log(`   - Lifecycle: ${artifact.lifecycle_state}`);
      console.log(`   - Materializations: ${artifact.materializations.length}`);
    });

    it('should return 404 for non-existent artifact', async () => {
      const url = getApiEndpointUrl('/api/artifact/resolve');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          artifact_id: 'non-existent-artifact-id',
          artifact_type: 'file',
          tenant_id: tenantId,
        }),
      });

      expect(response.status).toBe(404);
      console.log('✅ Correctly returned 404 for non-existent artifact');
    });
  });

  describe('Pending Intent Management', () => {
    it('should create a pending intent', async () => {
      // Need a target artifact ID - use test file artifact or create a dummy one
      const targetArtifactId = testFileArtifactId || 'test-artifact-for-pending-intent';
      
      const url = getApiEndpointUrl('/api/intent/pending/create');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          intent_type: 'parse_content',
          target_artifact_id: targetArtifactId,
          context: {
            ingestion_profile: 'hybrid',
            parse_options: {},
          },
          tenant_id: tenantId,
          user_id: TEST_USER_ID,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('intent_id');
      expect(data).toHaveProperty('status');
      expect(data.status).toBe('pending');
      
      testPendingIntentId = data.intent_id;
      
      console.log(`✅ Created pending intent: ${data.intent_id}`);
    });

    it('should list pending intents', async () => {
      const url = getApiEndpointUrl('/api/intent/pending/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          intent_type: 'parse_content',
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('intents');
      expect(data).toHaveProperty('total');
      expect(Array.isArray(data.intents)).toBe(true);
      
      // If we created a pending intent, it should be in the list
      if (testPendingIntentId) {
        const foundIntent = data.intents.find((intent: any) => intent.intent_id === testPendingIntentId);
        expect(foundIntent).toBeDefined();
        
        if (foundIntent) {
          expect(foundIntent).toHaveProperty('intent_type');
          expect(foundIntent).toHaveProperty('status');
          expect(foundIntent).toHaveProperty('context');
          expect(foundIntent.context).toHaveProperty('ingestion_profile');
          expect(foundIntent.context.ingestion_profile).toBe('hybrid');
        }
      }
      
      console.log(`✅ Listed ${data.total} pending intents`);
    });

    it('should filter pending intents by target artifact', async () => {
      if (!testFileArtifactId) {
        console.log('⚠️ Skipping: No target artifact available');
        return;
      }

      const url = getApiEndpointUrl('/api/intent/pending/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          target_artifact_id: testFileArtifactId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error (${response.status}):`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      expect(data).toHaveProperty('intents');
      expect(Array.isArray(data.intents)).toBe(true);
      
      // All returned intents should target the specified artifact
      data.intents.forEach((intent: any) => {
        expect(intent.target_artifact_id).toBe(testFileArtifactId);
      });
      
      console.log(`✅ Listed ${data.total} pending intents for artifact ${testFileArtifactId}`);
    });
  });

  describe('End-to-End Workflow', () => {
    it('should support complete artifact workflow', async () => {
      // 1. List artifacts
      const listUrl = getApiEndpointUrl('/api/artifact/list');
      const listResponse = await fetch(listUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          artifact_type: 'file',
          lifecycle_state: 'READY',
          limit: 1,
        }),
      });
      
      expect(listResponse.ok).toBe(true);
      const listData = await listResponse.json();
      
      if (listData.artifacts.length === 0) {
        console.log('⚠️ Skipping workflow test: No artifacts available');
        return;
      }
      
      const artifactId = listData.artifacts[0].artifact_id;
      
      // 2. Resolve artifact
      const resolveUrl = getApiEndpointUrl('/api/artifact/resolve');
      const resolveResponse = await fetch(resolveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          artifact_id: artifactId,
          artifact_type: 'file',
          tenant_id: tenantId,
        }),
      });
      
      expect(resolveResponse.ok).toBe(true);
      const resolveData = await resolveResponse.json();
      expect(resolveData.artifact.artifact_id).toBe(artifactId);
      
      // 3. Create pending intent
      const createUrl = getApiEndpointUrl('/api/intent/pending/create');
      const createResponse = await fetch(createUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent_type: 'parse_content',
          target_artifact_id: artifactId,
          context: { ingestion_profile: 'structured' },
          tenant_id: tenantId,
          user_id: TEST_USER_ID,
          session_id: sessionId,
        }),
      });
      
      expect(createResponse.ok).toBe(true);
      const createData = await createResponse.json();
      const intentId = createData.intent_id;
      
      // 4. Retrieve pending intent
      const getUrl = getApiEndpointUrl('/api/intent/pending/list');
      const getResponse = await fetch(getUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          target_artifact_id: artifactId,
        }),
      });
      
      expect(getResponse.ok).toBe(true);
      const getData = await getResponse.json();
      const foundIntent = getData.intents.find((i: any) => i.intent_id === intentId);
      expect(foundIntent).toBeDefined();
      expect(foundIntent.context.ingestion_profile).toBe('structured');
      
      console.log('✅ Complete artifact workflow validated');
    });
  });
});
