import { test, expect } from "@playwright/test";

test.describe("Operations Pillar E2E Tests", () => {
  test("should load the operations pillar page and show three choices", async ({
    page,
  }) => {
    await page.goto("/operations_pillar");
    await expect(page.locator("h1")).toContainText("Operations Pillar");
    await expect(page.getByText("Select Existing Files")).toBeVisible();
    await expect(page.getByText("Upload a New File")).toBeVisible();
    await expect(page.getByText("Create From Scratch")).toBeVisible();
  });

  test('should navigate to content pillar when "Upload a New File" is clicked', async ({
    page,
    browserName,
  }) => {
    if (browserName === "webkit") {
      await page.waitForLoadState("domcontentloaded");
    }
    await page.goto("/operations_pillar");
    await expect(page.locator("h1")).toContainText("Operations Pillar");
    await page.getByText("Upload a New File").click();
    await page.waitForURL(/.*content_pillar/);
    await expect(page).toHaveURL(/.*content_pillar/);
    await expect(page.locator("h1")).toContainText("Data Pillar");
  });

  test('should activate the blueprint wizard when "Create From Scratch" is clicked', async ({
    page,
  }) => {
    await page.goto("/operations_pillar");
    await expect(page.locator("h1")).toContainText("Operations Pillar");

    // Mock the wizard start endpoint
    await page.route("**/api/operations/wizard/start", async (route) => {
      await route.fulfill({
        json: { session_id: "wizard-session-123" },
      });
    });

    // Start waiting for the response BEFORE clicking
    const responsePromise = page.waitForResponse(
      "**/api/operations/wizard/start",
    );

    await page.getByRole("button", { name: /Create From Scratch/i }).click();

    // Wait for the API call to complete
    await responsePromise;

    await expect(page.getByText("Blueprint Wizard Activated")).toBeVisible();
    // Also check that the chat panel is now visible and ready
    await expect(
      page.getByText(/Please use the chat panel on your right/),
    ).toBeVisible();
  });

  test("should allow selecting and analyzing an existing SOP file", async ({
    page,
    browserName,
  }) => {
    if (browserName === "webkit") {
      await page.waitForLoadState("domcontentloaded");
    }
    // Mock the API response for fetching files BEFORE navigating
    await page.route("**/api/operations/files", async (route) => {
      await route.fulfill({
        json: {
          files: [
            { uuid: "sop-123", ui_name: "My Test SOP", file_type: "SOP" },
            {
              uuid: "wf-456",
              ui_name: "My Test Workflow",
              file_type: "workflow",
            },
          ],
        },
      });
    });

    // Mock the SOP-to-Workflow conversion
    await page.route("**/api/operations/sop-to-workflow", async (route) => {
      await route.fulfill({
        json: {
          nodes: [{ id: "1", data: { label: "Generated Node" } }],
          edges: [],
        },
      });
    });

    // Navigate to the page, which will trigger the files fetch
    await page.goto("/operations_pillar");
    await expect(page.locator("h1")).toContainText("Operations Pillar");

    // Click the button to show the selection UI
    await page.getByRole("button", { name: /Select Existing Files/i }).click();

    // The dropdowns should now be visible, so we can select from them
    await page.getByLabel("SOP File").selectOption({ label: "My Test SOP" });

    // Click the analyze button
    await page.getByRole("button", { name: "Analyze with AI" }).click();

    // Check for the generated workflow graph
    await expect(page.getByText("Generated Node")).toBeVisible();
  });
});
