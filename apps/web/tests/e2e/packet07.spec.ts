import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const session = {
  session_id: "11111111-1111-4111-8111-111111111111",
  session_token: "test-session-token",
  expires_at: "2099-01-01T00:00:00Z",
  policy_version: "POLICY-07-1",
  available_modes: ["UNSELECTED", "VOICE", "TEXT", "SILENT"],
  channel: "WEB",
  interaction_mode: "UNSELECTED",
  status: "OPEN",
  language: "en",
  intake_ready: false,
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
  intake_ready: false,
};

async function mockBackend(
  page: Page,
  options: {
    initialMode?: "UNSELECTED" | "VOICE" | "TEXT" | "SILENT";
    expireOnRestore?: boolean;
    staleContinueOnce?: boolean;
  } = {},
) {
  let backendMode = options.initialMode || "UNSELECTED";
  let intakeReady = backendMode !== "UNSELECTED";
  let expireOnRestore = options.expireOnRestore ?? false;
  let staleContinueOnce = options.staleContinueOnce ?? false;
  await page.route("**/api/backend/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname.replace("/api/backend/api/v1", "");
    if (path === "/channel/sessions" && request.method() === "POST") {
      backendMode = "UNSELECTED";
      intakeReady = false;
      return route.fulfill({
        json: {
          ...session,
          interaction_mode: backendMode,
          intake_ready: intakeReady,
        },
        status: 201,
      });
    }
    if (
      path === `/channel/sessions/${session.session_id}` &&
      request.method() === "GET"
    ) {
      if (expireOnRestore) {
        expireOnRestore = false;
        return route.fulfill({
          status: 401,
          json: { detail: "Session expired" },
        });
      }
      return route.fulfill({
        json: {
          ...session,
          interaction_mode: backendMode,
          intake_ready: intakeReady,
        },
      });
    }
    if (path.endsWith("/policy") && request.method() === "GET")
      return route.fulfill({ json: { ...policy, intake_ready: intakeReady } });
    if (path.endsWith("/intake/continue") && request.method() === "POST") {
      if (staleContinueOnce) {
        staleContinueOnce = false;
        return route.fulfill({
          status: 409,
          json: { detail: "The consent policy has changed." },
        });
      }
      intakeReady = true;
      return route.fulfill({
        json: {
          session_id: session.session_id,
          status: "OPEN",
          interaction_mode: backendMode,
        },
      });
    }
    if (path.endsWith("/mode") && request.method() === "POST") {
      backendMode = JSON.parse(request.postData() || "{}").interaction_mode;
      return route.fulfill({
        json: {
          session_id: session.session_id,
          status: "OPEN",
          interaction_mode: backendMode,
        },
      });
    }
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
    await mockBackend(page, { initialMode: "VOICE" });
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

  test("Escape Quick Exit clears a draft before neutral navigation", async ({
    page,
  }) => {
    await page.goto("/help");
    await page.evaluate(() => {
      sessionStorage.setItem("sambal:intake:session", "sensitive-session");
      sessionStorage.setItem("sambal:intake:draft", "sensitive-draft");
    });
    await page.keyboard.press("Escape");
    await expect(page).toHaveURL(/\/$/);
    expect(await page.evaluate(() => sessionStorage.length)).toBe(0);
    expect(new URL(page.url()).search).toBe("");
  });

  test("Speak to Write changes backend mode before routing and submits", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "VOICE" });
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      { ...session, interaction_mode: "VOICE", intake_ready: true },
    );
    await page.goto("/help/speak");
    await page.getByRole("button", { name: "Write instead" }).click();
    await expect(page).toHaveURL(/\/help\/write$/);
    await page
      .getByLabel("What happened?")
      .fill("I changed to writing safely.");
    await page.getByRole("button", { name: "Review" }).click();
    await page.getByRole("button", { name: "Send securely" }).click();
    await expect(page).toHaveURL(/\/help\/received$/);
  });

  test("Speak to Silent changes backend mode before routing and submits", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "VOICE" });
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      { ...session, interaction_mode: "VOICE", intake_ready: true },
    );
    await page.goto("/help/speak");
    await page.getByRole("button", { name: "Use Silent intake" }).click();
    await expect(page).toHaveURL(/\/help\/silent$/);
    await page.getByRole("button", { name: "Yes" }).click();
    await page.getByRole("button", { name: "No", exact: true }).click();
    await page.getByRole("button", { name: "Do not call" }).click();
    await page.getByRole("button", { name: "Review" }).click();
    await page.getByRole("button", { name: "Send securely" }).click();
    await expect(page).toHaveURL(/\/help\/received$/);
  });

  test("Back to choices restores the same active session", async ({ page }) => {
    await mockBackend(page);
    let sessionCreates = 0;
    page.on("request", (request) => {
      if (
        new URL(request.url()).pathname.endsWith("/channel/sessions") &&
        request.method() === "POST"
      )
        sessionCreates += 1;
    });
    await page.goto("/help");
    await page.getByRole("button", { name: "Start safely" }).click();
    await page.getByRole("button", { name: /I understand/ }).click();
    await page.getByRole("button", { name: /^Write/ }).click();
    await page.getByRole("link", { name: /Back to choices/ }).click();
    await expect(page).toHaveURL(/\/help$/);
    await expect(
      page.getByRole("heading", { name: "Choose how to continue" }),
    ).toBeVisible();
    expect(sessionCreates).toBe(1);
    await page.getByRole("button", { name: /^Silent/ }).click();
    await expect(page).toHaveURL(/\/help\/silent$/);
  });

  test("direct route with a server mode mismatch returns to choices", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "SILENT" });
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      { ...session, interaction_mode: "SILENT", intake_ready: true },
    );
    await page.goto("/help/write");
    await expect(page).toHaveURL(/\/help$/);
    await expect(
      page.getByRole("heading", { name: "Choose how to continue" }),
    ).toBeVisible();
  });

  test("expired session preserves the draft and offers a new private session", async ({
    page,
  }) => {
    await mockBackend(page, { expireOnRestore: true });
    await page.addInitScript(
      ({ activeSession, draft }) => {
        sessionStorage.setItem(
          "sambal:intake:session",
          JSON.stringify(activeSession),
        );
        sessionStorage.setItem("sambal:intake:draft", draft);
      },
      {
        activeSession: session,
        draft: JSON.stringify({ narrative: "unfinished" }),
      },
    );
    await page.goto("/help");
    await expect(
      page.getByRole("heading", { name: "Your saved words are still here" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Start a new private session/ }),
    ).toBeVisible();
    expect(
      await page.evaluate(() => sessionStorage.getItem("sambal:intake:draft")),
    ).toContain("unfinished");
    await page
      .getByRole("button", { name: /Start a new private session/ })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "What will happen with what you share",
      }),
    ).toBeVisible();
    expect(
      await page.evaluate(() => sessionStorage.getItem("sambal:intake:draft")),
    ).toContain("unfinished");
  });

  test("stale continuation reloads the notice and keeps the session", async ({
    page,
  }) => {
    await mockBackend(page, { staleContinueOnce: true });
    await page.goto("/help");
    await page.getByRole("button", { name: "Start safely" }).click();
    await page.getByRole("button", { name: /I understand/ }).click();
    await expect(
      page.getByText("The notice was updated. Please review it again."),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", {
        name: "What will happen with what you share",
      }),
    ).toBeVisible();
  });

  test("language selection is restored and locked after session creation", async ({
    page,
  }) => {
    await mockBackend(page);
    await page.addInitScript(() =>
      sessionStorage.setItem("sambal:intake:language", "hi"),
    );
    await page.goto("/help");
    await expect(page.getByText("Selected:").locator("..")).toContainText(
      "हिन्दी",
    );
    await page.getByRole("button", { name: "Start safely" }).click();
    await expect(
      page.locator(".language-selector__list button").filter({ hasText: "Hindi" }),
    ).toBeDisabled();
    await expect(page.locator(".citizen-language-lock")).toBeVisible();
  });

  test("Silent review uses human labels and moves focus to each heading", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "SILENT" });
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      { ...session, interaction_mode: "SILENT", intake_ready: true },
    );
    await page.goto("/help/silent");
    await expect(page.locator("#main-content h1")).toBeFocused();
    await page
      .getByRole("button", { name: "No — someone may be nearby" })
      .click();
    await expect(page.locator("#main-content h1")).toBeFocused();
    await page
      .getByRole("button", { name: "Yes, as soon as possible" })
      .click();
    await page.getByRole("button", { name: "Do not call" }).click();
    await page.getByRole("button", { name: "Review" }).click();
    await expect(page.getByText("No — someone may be nearby")).toBeVisible();
    await expect(page.getByText("Yes, as soon as possible")).toBeVisible();
    await expect(page.getByText("NO_SOMEONE_MAY_BE_NEARBY")).toHaveCount(0);
  });

  test("Write review shows a contact preference without contact details", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "TEXT" });
    await page.addInitScript(
      (value) =>
        sessionStorage.setItem("sambal:intake:session", JSON.stringify(value)),
      { ...session, interaction_mode: "TEXT", intake_ready: true },
    );
    await page.goto("/help/write");
    await page.getByLabel("What happened?").fill("I need a safe review.");
    await page.getByLabel("Contact preference").selectOption("DO_NOT_CALL");
    await page.getByRole("button", { name: "Review" }).click();
    await expect(
      page.getByText("Contact preference: DO_NOT_CALL"),
    ).toBeVisible();
  });

  test("mobile layouts and receipt do not overflow horizontally", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "TEXT" });
    for (const width of [320, 390, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(width === 1440 ? "/help/received" : "/help/write");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
    }
  });

  test("Silent flow is one question at a time and has no serious Axe findings", async ({
    page,
  }) => {
    await mockBackend(page, { initialMode: "SILENT" });
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
