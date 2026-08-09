import { expect, test } from "@playwright/test";

/**
 * What only a browser can prove.
 *
 * The API tests already assert the numbers. These assert that a person opening
 * the page actually SEES them — that the data reaches the DOM, that the warning
 * about the site's misleading label is visible rather than merely present, and
 * that the weekly grid renders both time bands. Duplicating the API assertions
 * here would buy nothing and cost seconds per run.
 */

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("renders the programme identity from the database", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "GradRadar", level: 1 })).toBeVisible();
  await expect(page.getByText(/Programa de Pós-Graduação em Ciência da Computação/)).toBeVisible();
  await expect(page.getByText(/CAPES 5/)).toBeVisible();
});

test("the schedule conflict is stated as a headline number", async ({ page }) => {
  const tile = page.locator("div", { hasText: /^Conflitam com sua jornada/ }).first();
  await expect(tile).toContainText("13/13");
  await expect(tile).toContainText("não há oferta noturna");
});

test("warns that the site label contradicts the real status", async ({ page }) => {
  // The behaviour the whole project exists for: the page must say the cycle is
  // closed even though the institution still calls it "Processo vigente".
  await expect(page.getByText(/encerrado/).first()).toBeVisible();
  const warning = page.getByText(/O site ainda rotula este processo como/);
  await expect(warning).toBeVisible();
  await expect(warning).toContainText("Processo vigente");
});

test("shows the admission timeline with dated stages", async ({ page }) => {
  await expect(page.getByText("CRONOGRAMA")).toBeVisible();
  await expect(page.getByText(/Análise documental/)).toBeVisible();
  await expect(page.getByText(/Entrevista estruturada/)).toBeVisible();
  await expect(page.getByText(/13 de mai\. a 19 de mai\./)).toBeVisible();
});

test("the weekly grid renders both bands and neither is in the evening", async ({ page }) => {
  const grid = page.locator("section", { hasText: "Grade semanal" });
  await expect(grid.getByText("08:00–12:00")).toBeVisible();
  await expect(grid.getByText("14:00–18:00")).toBeVisible();
  // Five weekday columns, no Saturday and no evening row.
  for (const day of ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]) {
    await expect(grid.getByText(day, { exact: true })).toBeVisible();
  }
  await expect(grid.getByText("Sábado")).toHaveCount(0);
});

test("the only AI offering of the term is visible with its professor", async ({ page }) => {
  const cell = page.locator("div", { hasText: /^CCO-724/ }).first();
  await expect(cell).toContainText("Aprendizado de Máquina");
  await expect(cell).toContainText("Tiago Agostinho de Almeida");
  await expect(cell).toContainText("AMPLN");
});

test("research lines are listed with their faculty counts", async ({ page }) => {
  const row = page.getByRole("row", { name: /AMPLN/ });
  await expect(row).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  await expect(row).toContainText("9");
});

test("is legible on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole("heading", { name: "GradRadar", level: 1 })).toBeVisible();
  // The grid scrolls inside its own container; the PAGE must not scroll sideways.
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  );
  expect(overflow).toBe(false);
});
