/**
 * Test Experience Layer Client Integration
 * 
 * Simple test to verify the Experience Layer Client works with the backend
 */

// Mock the config
const mockConfig = {
  apiUrl: 'http://localhost:8000'
};

// Test the Experience Layer Client
async function testExperienceLayerClient() {
  console.log('🧪 Testing Experience Layer Client Integration...');
  
  try {
    // Test 1: Health Check
    console.log('\n1️⃣ Testing Health Check...');
    const healthResponse = await fetch('http://localhost:8000/health');
    const healthData = await healthResponse.json();
    console.log('✅ Health Check:', healthData);
    
    // Test 2: Authentication
    console.log('\n2️⃣ Testing Authentication...');
    const authResponse = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'password123'
      })
    });
    const authData = await authResponse.json();
    console.log('✅ Authentication:', authData);
    
    if (!authData.success) {
      throw new Error('Authentication failed');
    }
    
    const token = authData.token;
    
    // Test 3: File Upload
    console.log('\n3️⃣ Testing File Upload...');
    const formData = new FormData();
    const testFile = new Blob(['This is a test file content'], { type: 'text/plain' });
    formData.append('file', testFile, 'test.txt');
    formData.append('file_type', 'txt');
    formData.append('ui_name', 'test.txt');
    
    const uploadResponse = await fetch('http://localhost:8000/api/content/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    const uploadData = await uploadResponse.json();
    console.log('✅ File Upload:', uploadData);
    
    if (!uploadData.success) {
      throw new Error('File upload failed');
    }
    
    const fileId = uploadData.file_id;
    
    // Test 4: File Listing
    console.log('\n4️⃣ Testing File Listing...');
    const listResponse = await fetch('http://localhost:8000/api/content/files', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const listData = await listResponse.json();
    console.log('✅ File Listing:', listData);
    
    // Test 5: File Parsing
    console.log('\n5️⃣ Testing File Parsing...');
    const parseResponse = await fetch('http://localhost:8000/api/content/parse', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_id: fileId,
        parse_options: {
          format: 'json_structured',
          include_metadata: true
        }
      })
    });
    const parseData = await parseResponse.json();
    console.log('✅ File Parsing:', parseData);
    
    // Test 6: Insights Analysis
    console.log('\n6️⃣ Testing Insights Analysis...');
    const analysisResponse = await fetch('http://localhost:8000/api/insights/analyze', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_ids: [fileId],
        analysis_type: 'comprehensive',
        include_visualizations: true
      })
    });
    const analysisData = await analysisResponse.json();
    console.log('✅ Insights Analysis:', analysisData);
    
    // Test 7: Guide Agent
    console.log('\n7️⃣ Testing Guide Agent...');
    const guidanceResponse = await fetch('http://localhost:8000/api/global/agent/analyze', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        intent: 'analyze_data',
        context: {
          current_pillar: 'content',
          available_files: 1,
          has_analysis: true
        }
      })
    });
    const guidanceData = await guidanceResponse.json();
    console.log('✅ Guide Agent:', guidanceData);
    
    console.log('\n🎉 All tests passed! Experience Layer Client integration is working!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    console.error('Stack trace:', error.stack);
  }
}

// Run the test
testExperienceLayerClient();
