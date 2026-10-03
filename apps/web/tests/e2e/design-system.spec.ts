import { expect, test } from "@playwright/test";

test.describe("Civic Calm design-system verification", () => {
  test("keyboard path reaches content, form, language control, and dialog", async ({
    page,
  }) => {
    await page.goto("/design-system");
    await page.keyboard.press("Tab");
    const skipLink = page.getByRole("link", { name: "Skip to main content" });
    await expect(skipLink).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();

    const reference = page.getByRole("textbox", {
      name: /Synthetic reference/,
    });
    await reference.focus();
    await page.keyboard.press("Control+A");
    await page.keyboard.type("DEMO-KEYBOARD-05");
    await expect(reference).toHaveValue("DEMO-KEYBOARD-05");

    const languageSearch = page.getByRole("searchbox", { name: "Language" });
    await languageSearch.focus();
    await page.keyboard.type("Urdu");
    await page.keyboard.press("Enter");
    await expect(page.getByText(/Selected:/)).toContainText("اردو");

    const trigger = page.getByRole("button", { name: "Remove example" });
    await trigger.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expect(trigger).toBeFocused();
  });

  test("320px viewport has no body overflow and keeps controls reachable", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 320, height: 700 });
    await page.goto("/design-system");
    const dimensions = await page.evaluate(() => ({
      body: document.body.scrollWidth,
      viewport: document.documentElement.clientWidth,
    }));
    expect(dimensions.body).toBeLessThanOrEqual(dimensions.viewport);
    await expect(page.getByRole("button", { name: "Continue" })).toBeVisible();
    await expect(
      page.getByRole("searchbox", { name: "Language" }),
    ).toBeVisible();
  });

  test("reduced motion disables nonessential animation", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/design-system");
    const duration = await page
      .locator(".skeleton")
      .first()
      .evaluate((element) => getComputedStyle(element).animationDuration);
    expect(["0.01ms", "0s"]).toContain(duration);
  });

  test("RTL example uses logical direction without clipping", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 800 });
    await page.goto("/design-system");
    const rtl = page.getByTestId("rtl-example");
    await expect(rtl).toHaveAttribute("dir", "rtl");
    const clipped = await rtl.evaluate(
      (element) => element.scrollWidth > element.clientWidth,
    );
    expect(clipped).toBe(false);
  });

  test("desktop content remains bounded", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/design-system");
    const width = await page
      .locator("#main-content")
      .evaluate((element) => Math.round(element.getBoundingClientRect().width));
    expect(width).toBeLessThanOrEqual(1280);
  });
});
