import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("SAMBAL Accessibility (a11y) Verification", () => {
  test("homepage has zero WCAG 2.1 AA violations", async ({ page }) => {
    await page.goto("/");

    // Wait for main content to be loaded
    await page.waitForSelector("#main-content");

    // Run Axe scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    // Assert zero accessibility violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test("design-system showcase has no serious or critical Axe violations", async ({
    page,
  }) => {
    await page.goto("/design-system");
    await page.waitForSelector("#main-content");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    const blocking = results.violations.filter((violation) =>
      ["serious", "critical"].includes(violation.impact ?? ""),
    );
    expect(blocking).toEqual([]);
  });
});
