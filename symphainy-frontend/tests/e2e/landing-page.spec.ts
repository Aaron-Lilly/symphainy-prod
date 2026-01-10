import { test, expect } from "@playwright/test";

test("landing page loads and displays welcome message", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText("Let's Build Your Coexistence Future"),
  ).toBeVisible();
});
