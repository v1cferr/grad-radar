import { expect, test, type Page } from "@playwright/test";

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

/** O PPGCC está atrás de uma aba porque está eliminado: quem abre a página
 *  precisa ver primeiro o que tem prazo. Os testes dele passam por aqui. */
async function openPpgcc(page: Page) {
  await page.getByRole("tab", { name: /PPGCC/ }).click();
  await expect(page.getByText(/Eliminado: não há oferta noturna/)).toBeVisible();
}

test("renders the search itself, not a single programme", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "GradRadar", level: 1 })).toBeVisible();
  // The subtitle states the four eliminatory requirements. It used to name the
  // PPGCC — which is eliminated, and led the page with a dead end.
  await expect(page.getByText(/presencial em São Carlos e com aula à noite/)).toBeVisible();
  await expect(page.getByText(/2 programas acompanhados/)).toBeVisible();
});

test("the open call leads the page, above everything else", async ({ page }) => {
  /**
   * The one thing here that is lost by not being seen in time. If this stops
   * being the first thing on the page, the project has failed at its only job.
   */
  const banner = page.locator("main > div").first();
  await expect(banner).toContainText("PPGPEP");
  await expect(banner).toContainText(/inscrições (abrem|abertas)/);
  await expect(banner).toContainText("14 de setembro de 2026");
  await expect(banner).toContainText("projeto de pesquisa");
  await expect(banner).toContainText(/dias? até fechar/);
});

test("seats that are not split by line say so instead of drawing empty bars", async ({ page }) => {
  const card = page.locator("div").filter({ hasText: /^PPGPEP · Mestrado/ }).first();
  await expect(
    page.getByText(/o edital não as distribui por linha de pesquisa/),
  ).toBeVisible();
  await expect(card).toBeVisible();
});

test("the schedule conflict is stated as a headline number", async ({ page }) => {
  await openPpgcc(page);
  const tile = page.locator("div", { hasText: /^Conflitam com sua jornada/ }).first();
  await expect(tile).toContainText("13/13");
  await expect(tile).toContainText("não há oferta noturna");
});

test("warns that the site label contradicts the real status", async ({ page }) => {
  await openPpgcc(page);
  // The behaviour the whole project exists for: the page must say the cycle is
  // closed even though the institution still calls it "Processo vigente".
  await expect(page.getByText(/encerrado/).first()).toBeVisible();
  const warning = page.getByText(/O site ainda rotula este processo como/);
  await expect(warning).toBeVisible();
  await expect(warning).toContainText("Processo vigente");
});

test("shows the admission timeline with dated stages", async ({ page }) => {
  await openPpgcc(page);
  await expect(page.getByText("CRONOGRAMA")).toBeVisible();
  await expect(page.getByText(/Análise documental/)).toBeVisible();
  await expect(page.getByText(/Entrevista estruturada/)).toBeVisible();
  await expect(page.getByText(/13 de mai\. a 19 de mai\./)).toBeVisible();
});

test("the weekly grid renders both bands and neither is in the evening", async ({ page }) => {
  await openPpgcc(page);
  const grid = page.locator("section", { hasText: "Grade semanal" });
  await expect(grid.getByText("08:00–12:00")).toBeVisible();
  await expect(grid.getByText("14:00–18:00")).toBeVisible();
  // Five weekday columns, no Saturday and no evening row.
  for (const day of ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]) {
    await expect(grid.getByText(day, { exact: true })).toBeVisible();
  }
  await expect(grid.getByText("Sábado")).toHaveCount(0);
});

/** The offering card itself. Selecting on the trigger slot matters: a plain
 *  `div` with hasText also matches the day-column container, and hovering THAT
 *  opens whichever sibling happens to sit under the cursor. */
const card = (page: Page, code: string) =>
  page.locator('[data-slot="tooltip-trigger"]', { hasText: code });

test("the only AI offering of the term is visible with its professor", async ({ page }) => {
  await openPpgcc(page);
  const cell = card(page, "CCO-724");
  await expect(cell).toContainText("Aprendizado de Máquina");
  await expect(cell).toContainText("Tiago Agostinho de Almeida");
});

test("hovering an offering reveals the detail the card omits", async ({ page }) => {
  // The card shows code, name and professor; everything else lives in the
  // tooltip, so this is the only place that proves the rest reaches the user.
  await openPpgcc(page);
  await card(page, "CCO-724").hover();

  // Base UI does not set role="tooltip" — the popup is identified by its slot.
  const tip = page.locator('[data-slot="tooltip-content"]');
  await expect(tip).toBeVisible();
  await expect(tip).toContainText("Machine Learning"); // the English name
  await expect(tip).toContainText("AMPLN");
  await expect(tip).toContainText("14:00–18:00");
  // Two rooms, because the same class runs at both campuses — and this one
  // ORIGINATES in Sorocaba.
  await expect(tip).toContainText("CCGT-1001");
  await expect(tip).toContainText("Conflita integralmente");
});

test("every research-line acronym explains itself on hover", async ({ page }) => {
  // The acronyms are opaque to anyone outside computing — and three people will
  // use this. Each must carry the official name, a plain gloss, and what the
  // line actually taught.
  await openPpgcc(page);
  const row = page.getByRole("row", { name: /AMPLN/ });
  await row.getByText("AMPLN").hover();

  const tip = page.locator('[data-slot="tooltip-content"]');
  await expect(tip).toBeVisible();
  await expect(tip).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  await expect(tip).toContainText("Ensinar computadores a aprender padrões");
  await expect(tip).toContainText("Docentes");
});

test("a line with no offering this term says so instead of showing nothing", async ({ page }) => {
  // BD taught nothing in 2026/2. An empty field would read as missing data;
  // the absence is itself the information.
  await openPpgcc(page);
  const row = page.getByRole("row", { name: /Banco de Dados/ });
  await row.getByText("BD", { exact: true }).hover();
  await expect(page.locator('[data-slot="tooltip-content"]')).toContainText(
    "nenhuma disciplina ofertada",
  );
});

test("research lines are listed with their faculty counts", async ({ page }) => {
  await openPpgcc(page);
  const row = page.getByRole("row", { name: /AMPLN/ });
  await expect(row).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  await expect(row).toContainText("9");
});

test("the eliminated programme is one click away, never the default", async ({ page }) => {
  /**
   * A regra que estrutura a página: o programa que não serve não pode ser a
   * primeira coisa que alguém lê. Antes disso, era.
   */
  await expect(page.getByRole("tab", { name: /PPGPEP/ })).toHaveAttribute("aria-selected", "true");
  await expect(page.getByText(/Aprendizado de Máquina e Processamento/)).toHaveCount(0);

  await openPpgcc(page);
  await expect(page.getByText(/Aprendizado de Máquina e Processamento/).first()).toBeVisible();
});

test("the edital is shown as actions, not as a wall of dates", async ({ page }) => {
  /**
   * A informação decisiva do edital não é uma data: é que o projeto de pesquisa
   * precisa estar escrito ANTES de a inscrição abrir. Se isso não estiver
   * visível, a página informa sem servir para nada.
   */
  const steps = page.getByText("O que fazer, em ordem");
  await expect(steps).toBeVisible();
  await expect(page.getByText(/três das quatro etapas acontecem/)).toBeVisible();

  // O primeiro passo vem aberto — é o que consome as quatro semanas.
  await expect(page.getByText(/É a única coisa avaliada/)).toBeVisible();

  const anexo = page.getByRole("button", { name: /declaração de vínculo/ });
  await anexo.click();
  await expect(page.getByText(/Anexo II/)).toBeVisible();
  await expect(page.getByText(/TOTI/).first()).toBeVisible();
});

test("the PPGPEP acronyms explain themselves too", async ({ page }) => {
  // O Victor pediu isto explicitamente: nem ele conhece as siglas, e o JP e o
  // César vão abrir a mesma página.
  const row = page.getByRole("row", { name: /TOTI/ });
  await row.getByText("TOTI", { exact: true }).hover();

  const tip = page.locator('[data-slot="tooltip-content"]');
  await expect(tip).toBeVisible();
  await expect(tip).toContainText("Trabalho, Organizações, Tecnologia e Inovação");
  await expect(tip).toContainText("adoção institucional de IA");
  // Não afirmar oferta que ninguém leu.
  await expect(tip).toContainText("grade ainda não transcrita");
});

test("the process timeline says when we will actually know", async ({ page }) => {
  const timeline = page.locator("div", { hasText: /^Do edital ao resultado/ }).first();
  await expect(timeline).toContainText("Inscrições");
  await expect(timeline).toContainText("Etapa 1");
  await expect(timeline).toContainText("Resultado");
  await expect(timeline).toContainText("18 de dez.");
});

test("shows what the monitor watches, and when it last looked", async ({ page }) => {
  const section = page.locator("section", { hasText: "Monitoramento" });
  await expect(section).toContainText("fontes oficiais monitoradas");
  // The one that 302s into SEI — the case a naive collector silently misses.
  await expect(section).toContainText("Calendário e disciplinas do semestre 2/2026");
  await expect(section).toContainText("grade horária (PDF)");
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
