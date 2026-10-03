import { test, expect } from "@playwright/test";

test.describe("SAMBAL Web Shell Smoke Tests", () => {
  test("homepage loads and displays correct metadata and headings", async ({
    page,
  }) => {
    await page.goto("/");

    // Check title
    await expect(page).toHaveTitle(
      /SAMBAL — Multilingual Trauma-Aware Intelligence & Response Layer/,
    );

    // Verify exactly one h1 is present
    const h1Count = await page.locator("h1").count();
    expect(h1Count).toBe(1);

    // Verify main heading content
    const h1 = page.locator("h1");
    await expect(h1).toContainText("SAMBAL Intelligence & Response Layer");

    // Verify header branding
    await expect(page.locator("header")).toContainText(
      "National Helpline Against Atrocities (14566)",
    );

    // Verify health button exists and is clickable
    const healthBtn = page.locator("#view-health-btn");
    await expect(healthBtn).toBeVisible();
  });

  test("health endpoint returns 200 OK with valid JSON structure", async ({
    request,
  }) => {
    const response = await request.get("/api/health");
    expect(response.status()).toBe(200);

    const json = await response.json();
    expect(json.status).toBe("ok");
    expect(json.service).toContain("SAMBAL");
  });
});
