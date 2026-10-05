import { expect, test } from "@playwright/test";

test("dashboard renders live platform state", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "Multi-Source State & Reconciliation" }),
  ).toBeVisible();
  await expect(page.getByText("API ok")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Source runs" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Cross-system decisions" }),
  ).toBeVisible();
  await expect(page.getByText("Acquire")).toBeVisible();
  await expect(page.getByText("Operate")).toBeVisible();

  await expect(page.getByText("github_api").first()).toBeVisible();
  await expect(page.getByText("pypi_api").first()).toBeVisible();
  await expect(page.getByText("MATCHED").first()).toBeVisible();
  await expect(page.getByText("github_repo:1362490").first()).toBeVisible();
  await expect(page.getByText("pypi_package:requests").first()).toBeVisible();

  const response = await page.request.get("/api/health");
  expect(response.ok()).toBeTruthy();
  await expect(response.json()).resolves.toEqual({ status: "ok" });

  await page.screenshot({
    path: "test-results/platform-dashboard.png",
    fullPage: true,
  });
});
