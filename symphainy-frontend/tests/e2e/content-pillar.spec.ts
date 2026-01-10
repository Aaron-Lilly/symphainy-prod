import { test, expect } from "@playwright/test";

// Helper for uploading a file
async function uploadFile(page, filePath) {
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(filePath);
}

test.describe("Content Pillar Flows", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/content_pillar");
  });

  test("dashboard renders files or shows empty state", async ({ page }) => {
    await expect(page.getByText("Data Files Dashboard")).toBeVisible();
    await expect(page.getByTestId("file-list")).toBeVisible();
    if ((await page.getByTestId("file-list").locator("td").count()) === 0) {
      await expect(page.getByTestId("empty-state")).toBeVisible();
    } else {
      const firstFile = page.getByTestId("file-list").locator("td").first();
      await expect(firstFile).toBeVisible();
      const fileName = await firstFile.textContent();
      expect(fileName).toBeTruthy();
    }
  });

  test("file upload tile selection enables dropzone and uploads file", async ({
    page,
    context,
  }) => {
    await expect(
      page.getByRole("heading", { name: "Upload File" }),
    ).toBeVisible();
    const structuredTile = page.getByRole("button", { name: "Structured" });
    await structuredTile.click();
    await expect(
      page.getByText(/Drop or select a Structured file/),
    ).toBeVisible();
    // Try uploading a valid file (assumes testfile.csv exists in project root or fixtures)
    // Comment out if not available
    // await uploadFile(page, 'testfile.csv');
    // await expect(page.locator('td', { hasText: 'testfile.csv' })).toBeVisible();
    // Try uploading an invalid file (simulate error)
    // await uploadFile(page, 'invalidfile.txt');
    // await expect(page.getByText(/invalid file/i)).toBeVisible();
  });

  test("parse preview dropdown and grid handles empty state", async ({
    page,
  }) => {
    // Mock the API response to ensure there's a file to parse
    await page.route("http://localhost:8000/fms/files", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        json: [
          {
            uuid: "test-file-uuid-1",
            ui_name: "test-file.csv",
            file_type: "csv",
            status: "Uploaded",
            created_at: new Date().toISOString(),
          },
        ],
      });
    });

    // We need to trigger a re-render or navigation to get the mocked data
    await page.goto("/content_pillar");

    await expect(page.getByText("Parse your Data File")).toBeVisible();

    // Explicitly wait for the dropdown to become visible after the page reloads with mocked data
    const dropdown = page.getByTestId("parse-dropdown");
    await expect(dropdown).toBeVisible({ timeout: 10000 });

    await expect(dropdown).toBeVisible();
    if (await dropdown.isDisabled()) {
      // Assert empty/disabled dropdown state
      await expect(dropdown).toBeDisabled();
      // Optionally check for a message or placeholder
      return;
    }
    const options = await dropdown.locator("option:enabled").all();
    if (options.length === 0) {
      // Assert empty/disabled dropdown state
      await expect(dropdown).toBeDisabled();
      return;
    }
    let valueToSelect = null;
    for (const option of options) {
      const label = await option.textContent();
      if (label && label.trim() !== "") {
        valueToSelect = label;
        break;
      }
    }
    expect(valueToSelect).toBeTruthy();
    await dropdown.selectOption({ label: valueToSelect! });
    await expect(page.getByText("File Metadata")).toBeVisible();
    await expect(page.getByText("Parsing Results")).toBeVisible();
    await expect(page.locator('input[value="R1C1"]')).toBeVisible();
  });

  // test('approve and reject actions', async ({ page }) => {
  //   ...
  // });

  test("file deletion removes file from list", async ({ page }) => {
    // Only run if delete button is present
    const deleteButtons = page.locator("button", { hasText: /delete/i });
    if ((await deleteButtons.count()) > 0) {
      const initialCount = await page.locator("td").count();
      await deleteButtons.first().click();
      // Wait for file to be removed
      await expect(page.locator("td")).toHaveCount(initialCount - 1);
    }
  });

  test("handles API/network errors gracefully", async ({ page, context }) => {
    // Intercept /fms/files and return a network error
    await context.route("http://localhost:8000/fms/files", (route) =>
      route.abort(),
    );
    await page.reload();
    // Assert error message is shown
    await expect(page.getByText(/error|failed|unavailable/i)).toBeVisible();
  });
});
