import { expect, test } from "@playwright/test";

test("a página hidrata sem erro de console", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));

  await page.goto("/", { waitUntil: "networkidle" });
  // Interage, para forçar hidratação de tudo que é client component.
  await page.getByRole("button", { name: /Ocultar \d+ eliminados/ }).click();
  await page.waitForTimeout(700);

  const hydration = errors.filter((e) => /hydrat|did not match|server rendered/i.test(e));
  expect(hydration, `erros de hidratação:\n${hydration.join("\n")}`).toEqual([]);
  expect(errors, `erros de console:\n${errors.join("\n")}`).toEqual([]);
});
