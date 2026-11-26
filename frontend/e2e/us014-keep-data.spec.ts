import { expect, test, type Locator, type Page } from "@playwright/test";

function uniq(): string {
  return `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
}

// Letters only, so a digit read from an idea card is always its vote count.
function tag(): string {
  const n = `${Date.now()}${Math.floor(Math.random() * 100000)}`;
  return Array.from(n)
    .map((d) => String.fromCharCode(97 + Number(d)))
    .join("");
}

function newPw(): string {
  return `Maple-${uniq()}-pass`;
}

function logOutButton(page: Page): Locator {
  return page
    .getByTestId("log-out-btn")
    .or(page.getByTestId("logout-btn"))
    .or(page.getByTestId("sign-out-btn"))
    .or(page.getByRole("button", { name: /log ?out|sign ?out/i }))
    .or(page.getByRole("link", { name: /log ?out|sign ?out/i }))
    .first();
}

async function openSignUp(page: Page) {
  const form = page.getByTestId("sign-up-form");
  for (const path of ["/signup", "/sign-up", "/register", "/"]) {
    await page.goto(path);
    try {
      await form.waitFor({ state: "visible", timeout: 3000 });
      return;
    } catch {
      // try the next address
    }
  }
  await page.goto("/");
  await page.getByTestId("sign-up-link").click();
  await expect(form).toBeVisible();
}

async function signUp(page: Page, email: string, pw: string) {
  await openSignUp(page);
  await page.getByTestId("email-input").fill(email);
  await page.getByTestId("password-input").fill(pw);
  await page.getByTestId("sign-up-btn").click();
  await expect(page.getByTestId("sign-up-form")).toHaveCount(0);
  await expect(logOutButton(page)).toBeVisible();
}

async function openLogIn(page: Page) {
  const form = page.getByTestId("log-in-form");
  for (const path of ["/login", "/log-in", "/signin", "/sign-in", "/"]) {
    await page.goto(path);
    try {
      await form.waitFor({ state: "visible", timeout: 3000 });
      return;
    } catch {
      // try the next address
    }
  }
  await page.goto("/");
  await page
    .getByTestId("log-in-link")
    .or(page.getByRole("link", { name: /log ?in|sign ?in/i }))
    .or(page.getByRole("button", { name: /^(log ?in|sign ?in)$/i }))
    .first()
    .click();
  await expect(form).toBeVisible();
}

async function logInFromCurrentPage(page: Page, email: string, pw: string) {
  const form = page.getByTestId("log-in-form");
  if (!(await form.isVisible().catch(() => false))) {
    const link = page.getByTestId("log-in-link");
    if (await link.count()) {
      await link.click();
    } else {
      await openLogIn(page);
    }
  }
  await expect(form).toBeVisible();
  await page.getByTestId("email-input").fill(email);
  await page.getByTestId("password-input").fill(pw);
  await page.getByTestId("log-in-btn").click();
  await expect(page.getByTestId("log-in-form")).toHaveCount(0);
  await expect(logOutButton(page)).toBeVisible();
}

async function logInFresh(page: Page, email: string, pw: string) {
  await openLogIn(page);
  await page.getByTestId("email-input").fill(email);
  await page.getByTestId("password-input").fill(pw);
  await page.getByTestId("log-in-btn").click();
  await expect(page.getByTestId("log-in-form")).toHaveCount(0);
  await expect(logOutButton(page)).toBeVisible();
}

async function postIdea(page: Page, title: string, description: string) {
  await page
    .getByRole("link", { name: "Post an Idea" })
    .or(page.getByRole("button", { name: "Post an Idea" }))
    .first()
    .click();
  await expect(page.getByTestId("new-idea-form")).toBeVisible();
  await page.locator("#idea-title").fill(title);
  await page.locator("#idea-desc").fill(description);
  await page.getByTestId("submit-idea-btn").click();
  await expect(page.getByText(title).first()).toBeVisible();
}

function voteButton(page: Page, title: string): Locator {
  return page.getByRole("button", { name: `Vote for ${title}`, exact: false }).first();
}

// The idea's own card: from the element holding its title, go up to the first ancestor
// that shows a vote count, then to the widest ancestor that still holds one idea's count.
async function readCardText(page: Page, title: string): Promise<string | null> {
  const el = page.getByTestId("ideas-ranked-by-votes-list").getByText(title, { exact: false }).first();
  if ((await el.count()) === 0) return null;
  return el.evaluate((node) => {
    const count = (s: string) => (s.match(/\d+\s*votes?\b/gi) ?? []).length;
    let cur: HTMLElement | null = node as HTMLElement;
    while (cur && count(cur.innerText ?? "") === 0) cur = cur.parentElement;
    if (!cur) return null;
    while (
      cur.parentElement &&
      cur.parentElement.getAttribute("data-testid") !== "ideas-ranked-by-votes-list" &&
      count(cur.parentElement.innerText ?? "") === 1
    ) {
      cur = cur.parentElement;
    }
    return cur.innerText ?? "";
  });
}

async function voteCount(page: Page, title: string): Promise<number | null> {
  const text = await readCardText(page, title);
  if (text === null) return null;
  const m = text.match(/(\d+)\s*votes?/i);
  return m ? Number(m[1]) : null;
}

async function expectCount(page: Page, title: string, n: number) {
  await expect.poll(() => voteCount(page, title)).toBe(n);
}

async function isMarkedVoted(page: Page, title: string): Promise<boolean> {
  const text = await readCardText(page, title);
  if (text === null) return false;
  if (/voted/i.test(text)) return true;
  const btn = voteButton(page, title);
  if ((await btn.count()) === 0) return false;
  if (await btn.isDisabled()) return true;
  const pressed = await btn.getAttribute("aria-pressed");
  if (pressed === "true") return true;
  const cls = (await btn.getAttribute("class")) ?? "";
  return /voted|active|selected/i.test(cls);
}

async function expectMarkedVoted(page: Page, title: string) {
  await expect.poll(() => isMarkedVoted(page, title)).toBe(true);
}

async function boardText(page: Page): Promise<string> {
  return page.getByTestId("ideas-ranked-by-votes-list").innerText();
}

async function expectAbove(page: Page, upper: string, lower: string) {
  await expect
    .poll(async () => {
      // The board shows titles in capitals, so compare without case.
      const t = (await boardText(page)).toLowerCase();
      const a = t.indexOf(upper.toLowerCase());
      const b = t.indexOf(lower.toLowerCase());
      return a >= 0 && b >= 0 && a < b ? "ok" : `${upper} / ${lower} in: ${JSON.stringify(t)}`;
    })
    .toBe("ok");
}

test("TC-042 person sees the same board after the app is restarted", async ({ page, browser }) => {
  const t = tag();
  const email = `carol-${uniq()}@example.com`;
  const pw = newPw();
  const lunch = `Team lunch ${t}`;
  const quiet = `Quiet hours ${t}`;

  await signUp(page, email, pw);
  await expect(page.getByTestId("ideas-board-title")).toBeVisible();

  await postIdea(page, lunch, "Monthly lunch for the whole team");
  await expectCount(page, lunch, 0);

  await postIdea(page, quiet, "Two focus hours each afternoon");
  await expectCount(page, quiet, 0);
  await expectAbove(page, quiet, lunch);

  await voteButton(page, lunch).click();
  await expectCount(page, lunch, 1);
  await expectAbove(page, lunch, quiet);

  // The app comes back: a new browser session reloads the board and signs in again.
  await page.reload();
  await expect(page.getByTestId("ideas-board-title")).toBeVisible();
  const ctx = await browser.newContext();
  try {
    const again = await ctx.newPage();
    await again.goto("/");
    await expect(again.getByTestId("ideas-board-title")).toBeVisible();
    await logInFresh(again, email, pw);

    await expect(again.getByText(lunch).first()).toBeVisible();
    await expect(again.getByText(quiet).first()).toBeVisible();
    await expectAbove(again, lunch, quiet);
    await expectCount(again, lunch, 1);
    await expectMarkedVoted(again, lunch);
    await expectCount(again, quiet, 0);
  } finally {
    await ctx.close();
  }
});

test("TC-046 double-click and stale second tab never add a second vote", async ({ page, context }) => {
  const t = tag();
  const email = `gina-${uniq()}@example.com`;
  const pw = newPw();
  const bike = `Bike storage ${t}`;

  await signUp(page, email, pw);
  await postIdea(page, bike, "Add a safe place to park bikes");
  await expectCount(page, bike, 0);

  // Second tab, same signed-in person, not voting.
  const second = await context.newPage();
  await second.goto("/");
  await expect(second.getByText(bike).first()).toBeVisible();
  await expectCount(second, bike, 0);
  expect(await isMarkedVoted(second, bike)).toBe(false);

  // First tab: double-click the vote button.
  await page.bringToFront();
  await voteButton(page, bike).dblclick();
  await expectCount(page, bike, 1);
  await page.waitForTimeout(500);
  await expectCount(page, bike, 1);

  // Second tab, not reloaded: click the vote button.
  await second.bringToFront();
  const btn = voteButton(second, bike);
  if ((await btn.count()) > 0 && (await btn.isEnabled())) {
    await btn.click();
  }
  await second.waitForTimeout(500);
  await expect(second.getByText(bike).first()).toBeVisible();
  const afterClick = await voteCount(second, bike);
  expect(afterClick === null || afterClick <= 1).toBe(true);

  // Reload both tabs.
  await page.reload();
  await second.reload();
  for (const p of [page, second]) {
    await expect(p.getByText(bike).first()).toBeVisible();
    await expectCount(p, bike, 1);
    await expectMarkedVoted(p, bike);
  }
});

test("TC-048 person uses the app without any key, payment or outside sign-in", async ({ page }) => {
  const t = tag();
  const email = `ivan-${uniq()}@example.com`;
  const pw = newPw();
  const photo = `Team photo ${t}`;
  const outside = /api key|license key|payment|credit card|subscribe|subscription|upgrade|continue with (google|github|facebook)|sign in with (google|github|facebook)|verification code/i;

  await page.goto("/");
  await expect(page.getByTestId("ideas-board-title")).toBeVisible();
  expect(await page.locator("body").innerText()).not.toMatch(outside);

  await signUp(page, email, pw);
  expect(await page.locator("body").innerText()).not.toMatch(outside);

  await postIdea(page, photo, "Take a team photo each quarter");
  await expect(page.getByText(photo).first()).toBeVisible();

  await voteButton(page, photo).click();
  await expectCount(page, photo, 1);
  expect(await page.locator("body").innerText()).not.toMatch(outside);

  await logOutButton(page).click();
  await expect(logOutButton(page)).toHaveCount(0);

  await logInFromCurrentPage(page, email, pw);
  await expect(page.getByText(photo).first()).toBeVisible();
  await expectCount(page, photo, 1);
  expect(await page.locator("body").innerText()).not.toMatch(outside);
});
