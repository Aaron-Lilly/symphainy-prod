import { test, expect } from "@playwright/test";

// Helper to mock backend API responses for Insights orchestrator/agent
async function mockAgentResponse(page, responses) {
  await page.route("**/global/agent", (route) => {
    console.log(
      "[mockAgentResponse] Intercepted request:",
      route.request().url(),
    );
    console.log("[mockAgentResponse] Sending mock response:", { responses });
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ responses }),
    });
  });
}

// Helper to mock file list and session API
async function mockFileListAndSession(page) {
  await page.route("http://localhost:8000/fms/files", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          uuid: "test-file-uuid",
          ui_name: "Test File",
          file_type: "csv",
          created_at: new Date().toISOString(),
          status: "parsed",
          parsed_path: "/files/test-file.csv",
          metadata: { rows: 10, columns: 2 },
        },
      ]),
    });
  });
  await page.route("**/insights/session", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session_token: "test-session-token",
        message: "Session started",
      }),
    });
  });
}

test.describe("Insights Panel (new schema)", () => {
  test.beforeEach(async ({ page }) => {
    // Mock file/session as before...
    await page.route("http://localhost:8000/fms/files", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            uuid: "test-file-uuid",
            ui_name: "Test File",
            file_type: "csv",
            created_at: new Date().toISOString(),
            status: "parsed",
            parsed_path: "/files/test-file.csv",
            metadata: { rows: 10, columns: 2 },
          },
        ]),
      });
    });
    await page.route("**/insights/session", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          session_token: "test-session-token",
          message: "Session started",
        }),
      });
    });
  });

  test("renders all output sections from new schema", async ({ page }) => {
    await page.route("**/global/agent", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          responses: [
            { type: "summary_output", summary: "Test summary" },
            {
              type: "data_grid_response",
              columnDefs: [{ headerName: "id", field: "id" }],
              rowData: [{ id: 1 }, { id: 2 }],
            },
            {
              type: "visual_output",
              title: "Test Chart",
              description: "Chart",
              data: [{ x: "A", y: 1 }],
              nivoChartType: "bar",
            },
            { type: "agent_message", content: "Test agent message" },
            { type: "error", message: "Test alert", error: "Do something" },
          ],
        }),
      });
    });
    await page.goto("/insights_pillar");
    await expect(page.getByText("Loading files...")).not.toBeVisible({
      timeout: 15000,
    });
    await page.getByTestId("file-card").click();
    await page.getByRole("button", { name: "Analyze with AI" }).click();
    await expect(
      page.getByRole("heading", { name: "Data Insights", level: 1 }),
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId("section-summary")).toContainText(
      "Test summary",
    );
    await expect(page.getByTestId("section-data-grid")).toContainText("id");
    await expect(page.getByTestId("section-visualizations")).toContainText(
      "Test Chart",
    );
    await expect(page.getByTestId("section-alerts")).toContainText(
      "Test alert",
    );
    await expect(page.getByTestId("section-alerts")).toContainText(
      "Do something",
    );
  });

  test("handles missing summary gracefully", async ({ page }) => {
    await page.route("**/global/agent", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          responses: [
            // No summary_output
            {
              type: "data_grid_response",
              columnDefs: [{ headerName: "id", field: "id" }],
              rowData: [{ id: 1 }],
            },
          ],
        }),
      });
    });
    await page.goto("/insights_pillar");
    await expect(page.getByText("Loading files...")).not.toBeVisible({
      timeout: 15000,
    });
    await page.getByTestId("file-card").click();
    await page.getByRole("button", { name: "Analyze with AI" }).click();
    await expect(page.getByTestId("section-summary")).toContainText(
      "No summary available.",
    );
  });

  test("handles empty responses array", async ({ page }) => {
    await page.route("**/global/agent", (route) => {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ responses: [] }),
      });
    });
    await page.goto("/insights_pillar");
    await expect(page.getByText("Loading files...")).not.toBeVisible({
      timeout: 15000,
    });
    await page.getByTestId("file-card").click();
    await page.getByRole("button", { name: "Analyze with AI" }).click();
    await expect(page.getByTestId("section-summary")).toContainText(
      "No summary available.",
    );
    await expect(page.getByTestId("section-data-grid")).toContainText(
      "No columns.",
    );
    await expect(page.getByTestId("section-visualizations")).toContainText(
      "No visualizations available.",
    );
    await expect(page.getByTestId("section-alerts")).toContainText(
      "No alerts.",
    );
  });

  test("handles backend/network error gracefully", async ({ page }) => {
    await page.route("**/global/agent", (route) => {
      route.abort();
    });
    await page.goto("/insights_pillar");
    await expect(page.getByText("Loading files...")).not.toBeVisible({
      timeout: 15000,
    });
    await page.getByTestId("file-card").click();
    await page.getByRole("button", { name: "Analyze with AI" }).click();
    await expect(page.getByText("Failed to load insights.")).toBeVisible();
  });
});
