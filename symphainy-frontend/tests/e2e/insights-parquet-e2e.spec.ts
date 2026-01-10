import { test, expect } from "@playwright/test";
import path from "path";

// test.describe('Full Data-to-Insights E2E Flow', () => {
//   const csvPath = path.resolve(__dirname, 'dummydataforinsights.csv');

//   test('uploads csv, parses, navigates to insights, and generates all outputs including heatmap', async ({ page }) => {
//     // 1. Data tab: upload file
//     await page.goto('/content_pillar');

//     // Select the 'Structured' file type to enable the dropzone
//     await page.getByRole('button', { name: 'Structured' }).click();

//     // Upload the file
//     await page.locator('input[type="file"]').setInputFiles(csvPath);

//     // Assert that the upload button is now visible and click it
//     const uploadButton = page.getByRole('button', { name: 'Upload' });
//     await expect(uploadButton).toBeVisible();
//     await uploadButton.click();

//     // Wait for and assert the success message
//     await expect(page.getByText('Upload successful!')).toBeVisible();

//     // 2. Navigate to Insights and find the file
//     await page.goto('/insights_pillar');
//     await expect(page.getByText('Test File')).toBeVisible(); // Or whatever ui_name is used
//     await page.getByRole('button', { name: 'Analyze with AI' }).click();

//     // 3. Mock the agent response for this specific test
//     await page.route('**/global/agent', async route => {
//       route.fulfill({
//         status: 200,
//         contentType: 'application/json',
//         body: JSON.stringify({
//           responses: [
//             { type: 'summary_output', summary: 'This is a test summary for the E2E flow.' },
//             { type: 'visual_output', title: 'E2E Heatmap', description: 'A test heatmap.', data: [ { "id": "A", "data": [{ "x": "1", "y": 10 }] } ], nivoChartType: 'heatmap' }
//           ]
//         })
//       });
//     });

//     // 4. Assert that the insights are generated
//     await expect(page.getByTestId('section-summary')).toContainText('This is a test summary');
//     await expect(page.getByTestId('section-visualizations')).toContainText('E2E Heatmap');
//     // Add check for heatmap canvas element
//     await expect(page.locator('.nivo-heatmap canvas')).toBeVisible();
//   });
// });
