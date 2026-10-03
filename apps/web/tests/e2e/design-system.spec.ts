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

    const languageSearch = page.getByRole("combobox", { name: "Language" });
    await expect(languageSearch).toHaveAttribute("aria-controls");
    await languageSearch.focus();
    await page.keyboard.type("Urdu");
    await expect(languageSearch).toHaveAttribute(
      "aria-activedescendant",
      /option-ur/,
    );
    await page.keyboard.press("Enter");
    await expect(page.getByText(/Selected:/)).toContainText("اردو");

    const trigger = page.getByRole("button", { name: "Remove example" });
    await trigger.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Close dialog" }),
    ).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expect(trigger).toBeFocused();
  });

  test("tooltip has one focus stop and invalid form recovery is keyboard usable", async ({
    page,
  }) => {
    await page.goto("/design-system");

    const tooltipTrigger = page.getByRole("button", { name: "More context" });
    await tooltipTrigger.focus();
    await expect(tooltipTrigger).toHaveAttribute("aria-describedby");
    await expect(page.getByRole("tooltip")).toBeAttached();
    await page.keyboard.press("Tab");
    await expect(page.locator(".popover summary")).toBeFocused();

    const submit = page.getByRole("button", {
      name: "Submit synthetic invalid form",
    });
    await submit.focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("heading", {
        name: "Please check the highlighted fields",
      }),
    ).toBeFocused();
    await page.keyboard.press("Tab");
    await page.keyboard.press("Enter");
    await expect(page.locator("#synthetic-contact")).toBeFocused();
  });

  test("language combobox keeps active descendant safe when no options match", async ({
    page,
  }) => {
    await page.goto("/design-system");
    const search = page.getByRole("combobox", { name: "Language" });
    await search.fill("no language matches this");
    await expect(search).not.toHaveAttribute("aria-activedescendant");
    await page.keyboard.press("ArrowDown");
    await expect(search).not.toHaveAttribute("aria-activedescendant");
  });

  test("language options remain virtualized from the Tab order", async ({
    page,
  }) => {
    await page.goto("/design-system");
    const search = page.getByRole("combobox", { name: "Language" });
    const options = page.locator('.language-selector [role="option"]');
    await expect(options.first()).toHaveAttribute("tabindex", "-1");
    await search.focus();
    await page.keyboard.press("ArrowDown");
    await expect(search).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(page.locator('[role="option"]:focus')).toHaveCount(0);
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
      page.getByRole("combobox", { name: "Language" }),
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
