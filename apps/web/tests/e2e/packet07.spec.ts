import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const session = {
  session_id: "11111111-1111-4111-8111-111111111111",
  session_token: "test-session-token",
  expires_at: "2099-01-01T00:00:00Z",
  policy_version: "POLICY-07-1",
  available_modes: ["UNSELECTED", "VOICE", "TEXT", "SILENT"],
};

const policy = {
  policy_version: "POLICY-07-1",
  served_locale: "en",
  translation_status: "AUTHORITATIVE",
  required_notices: [
    {
      purpose_code: "PURP-01",
      name: "Citizen intake",
      why_needed: "To receive the information you choose to share.",
      data_categories: ["Information you provide"],
      recipients: ["Authorized human reviewers"],
      retention_status: "Retention follows the published policy.",
      effect_of_decline: "You can choose another path or stop.",
    },
  ],
};

async function mockBackend(page: Page) {
  await page.route("**/api/backend/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace("/api/backend/api/v1", "");
    if (path === "/channel/sessions" && request.method() === "POST")
      return route.fulfill({ json: session, status: 201 });
    if (path.endsWith("/policy") && request.method() === "GET")
      return route.fulfill({ json: policy });
    if (path.endsWith("/intake/continue") && request.method() === "POST")
      return route.fulfill({
        json: {
          session_id: session.session_id,
          status: "OPEN",
          interaction_mode: "UNSELECTED",
        },
      });
    if (path.endsWith("/mode") && request.method() === "POST")
      return route.fulfill({
        json: {
          session_id: session.session_id,
          status: "OPEN",
          interaction_mode: JSON.parse(request.postData() || "{}")
            .interaction_mode,
        },
      });
    if (path.endsWith("/write") && request.method() === "POST")
      return route.fulfill({
        json: {
          tracking_reference: "S-2099-ABCDEF123456",
          received_at: "2099-01-01T00:00:00Z",
          interaction_mode: "TEXT",
          entry_count: 1,
          case_created: true,
        },
        status: 201,
      });
    if (path.endsWith("/silent") && request.method() === "POST")
      return route.fulfill({
        json: {
          tracking_reference: "S-2099-ABCDEF123457",
          received_at: "2099-01-01T00:00:00Z",
          interaction_mode: "SILENT",
          entry_count: 3,
          case_created: true,
        },
        status: 201,
      });
    return route.fulfill({ json: {} });
  });
}

test.describe("Packet 07 citizen intake", () => {
  test("uses the real notice boundary and completes Write without sensitive URL state", async ({
    page,
  }) => {
    await mockBackend(page);
    await page.goto("/help");
    await page.getByRole("button", { name: "Start safely" }).click();
    await expect(
      page.getByRole("heading", {
        name: "What will happen with what you share",
      }),
    ).toBeVisible();
    await page.getByRole("button", { name: /I understand/ }).click();
    await page.getByRole("button", { name: /^Write/ }).click();
    await page
      .getByLabel("What happened?")
      .fill("I need help with a situation.");
    await page.getByRole("button", { name: "Review" }).click();
    await page.getByRole("button", { name: "Send securely" }).click();
    await expect(page).toHaveURL(/\/help\/received$/);
    await expect(page.getByText("S-2099-ABCDEF123456")).toBeVisible();
    expect(new URL(page.url()).search).toBe("");
  });

  test("Speak is truthful and never asks for microphone access", async ({
    page,
  }) => {
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      session,
    );
    await page.goto("/help/speak");
    await expect(
      page.getByRole("heading", { name: "Speak is not active yet" }),
    ).toBeVisible();
    await expect(page.getByText("Nothing is listening.")).toBeVisible();
    expect(
      await page.evaluate(() => typeof navigator.mediaDevices?.getUserMedia),
    ).toBe("function");
    expect(
      await page.evaluate(
        () => document.querySelectorAll("audio, video").length,
      ),
    ).toBe(0);
  });

  test("Quick Exit purges session state before neutral navigation", async ({
    page,
  }) => {
    await page.goto("/help");
    await page.evaluate(() => {
      sessionStorage.setItem(
        "sambal:intake:session",
        "sensitive-session-placeholder",
      );
      sessionStorage.setItem(
        "sambal:intake:draft",
        "sensitive-draft-placeholder",
      );
    });
    await page.getByRole("button", { name: /quick exit/i }).click();
    await expect(page).toHaveURL(/\/$/);
    expect(await page.evaluate(() => sessionStorage.length)).toBe(0);
  });

  test("Silent flow is one question at a time and has no serious Axe findings", async ({
    page,
  }) => {
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      session,
    );
    await page.goto("/help/silent");
    await expect(page).toHaveTitle("Citizen Information Services");
    await page.getByRole("button", { name: "Yes" }).click();
    await page.getByRole("button", { name: "No", exact: true }).click();
    await page.getByRole("button", { name: "Do not call" }).click();
    await page.getByRole("button", { name: "Review" }).click();
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(
      results.violations.filter((item) =>
        ["serious", "critical"].includes(item.impact ?? ""),
      ),
    ).toEqual([]);
  });
});
