import { test, expect } from "@playwright/test";

const MOCK_PROPOSAL = {
  title: "POC Proposal: AI-Enhanced Customer Support & Sales Reporting",
  executive_summary:
    "This document outlines a 90-day proof-of-concept (POC) to demonstrate the value of integrating SymphAIny's AI capabilities into your existing customer support and sales workflows.",
  opportunity_statement:
    "Currently, customer support resolution times are high due to manual information retrieval, and the sales team spends over 20 hours per week on manual reporting tasks. This POC will address these inefficiencies directly.",
  poc_scope: [
    "Integrate a chatbot into the main support channel.",
    "Develop an automated sales report generator.",
    "Create a real-time dashboard for key support and sales metrics.",
  ],
  poc_goals: [
    "Reduce average support ticket resolution time by 30%.",
    "Eliminate 95% of manual sales reporting effort.",
    "Provide leadership with on-demand visibility into performance.",
  ],
  next_steps:
    "Upon approval, we will schedule a kickoff meeting to finalize the technical details and assign resources. The target start date for the POC is two weeks from approval.",
};

test.describe("Experience Pillar", () => {
  test("should load the page and allow a user to generate a proposal", async ({
    page,
  }) => {
    // Mock the successful API response
    await page.route(
      "http://localhost:8000/api/experience/start",
      async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          json: {
            session_id: "mock-experience-session-id",
            data: MOCK_PROPOSAL,
            message: "Analysis complete.",
          },
        });
      },
    );

    // Navigate to the page
    await page.goto("/experience_pillar");

    // Check for the initial state
    await expect(
      page.getByRole("heading", { name: "Your Coexistence Journey" }),
    ).toBeVisible();
    await expect(page.getByText("Begin Your Analysis")).toBeVisible();

    // Click the button to start analysis
    await page.getByRole("button", { name: "Start Analysis" }).click();

    // Check that the proposal is rendered correctly
    await expect(
      page.getByRole("heading", { name: MOCK_PROPOSAL.title }),
    ).toBeVisible({ timeout: 10000 }); // Increased timeout for robustness
    await expect(page.getByText(MOCK_PROPOSAL.executive_summary)).toBeVisible();
    await expect(
      page.getByText("Reduce average support ticket resolution time by 30%."),
    ).toBeVisible();
  });

  test("should display an error message if the analysis fails", async ({
    page,
  }) => {
    // Mock the failed API response
    await page.route(
      "http://localhost:8000/api/experience/start",
      async (route) => {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          json: { detail: "A critical error occurred during analysis." },
        });
      },
    );

    // Navigate to the page
    await page.goto("/experience_pillar");

    // Click the button to start analysis
    await page.getByRole("button", { name: "Start Analysis" }).click();

    // Check that the error message is displayed
    await expect(
      page.getByText("A critical error occurred during analysis."),
    ).toBeVisible();
  });
});
