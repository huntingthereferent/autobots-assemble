import { expect, test } from "@playwright/test";

test("dashboard renders persisted browser fixture state", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Multi-Source State & Reconciliation" }),
  ).toBeVisible();
  await expect(page.getByText("API ok")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Source runs" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Cross-system decisions" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Current identity state" }),
  ).toBeVisible();
  await expect(page.getByText("Acquire")).toBeVisible();
  await expect(page.getByText("Operate")).toBeVisible();

  await expect(page.getByText("github_api").first()).toBeVisible();
  await expect(page.getByText("pypi_api").first()).toBeVisible();
  await expect(page.getByText("MATCHED").first()).toBeVisible();
  await expect(page.getByText("github_repo:1362490").first()).toBeVisible();
  await expect(page.getByText("pypi_package:requests").first()).toBeVisible();
  await expect(page.getByText("github_repo:1362490").last()).toBeVisible();
  await expect(page.getByText("pypi_package:requests").last()).toBeVisible();
  await expect(page.getByText("present").first()).toBeVisible();

  const response = await page.request.get("/api/health");
  expect(response.ok()).toBeTruthy();
  await expect(response.json()).resolves.toEqual({ status: "ok" });

  await page.screenshot({
    path: "test-results/platform-dashboard.png",
    fullPage: true,
  });
});


// Each section must keep its own evidence status. An HTTP error is not an empty list.
test("identity endpoint failure leaves other evidence visible", async ({ page }) => {
  await page.route("**/api/identity/decisions?limit=8", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "temporarily unavailable" }),
    }),
  );
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Identity decisions");
  await expect(page.getByText("Identity decisions unavailable.")).toBeVisible();
  await expect(page.locator(".stat").filter({ hasText: "Identity matches" }).locator("strong")).toHaveText("—");
  await expect(page.getByText("github_api").first()).toBeVisible();
  await expect(page.getByText("present").first()).toBeVisible();
  await expect(page.getByText("API ok")).toBeVisible();
});

// JSON that is not the expected collection is missing evidence, never zero.
test("invalid source-run response cannot break the dashboard", async ({ page }) => {
  await page.route("**/api/ops/source-runs?limit=12", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ error: "invalid source payload" }),
    }),
  );
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Source runs");
  await expect(page.getByText("Source runs unavailable.")).toBeVisible();
  await expect(page.locator(".stat").filter({ hasText: "Recent source runs" }).locator("strong")).toHaveText("—");
  await expect(page.getByText("MATCHED").first()).toBeVisible();
  await expect(page.getByText("API ok")).toBeVisible();
});
