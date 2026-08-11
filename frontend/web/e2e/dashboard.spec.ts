import { expect, test, type Locator, type Page } from "@playwright/test";

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
  /**
   * `networkidle` e não o default: um `hover()` disparado ANTES da hidratação é
   * perdido — o Base UI ainda não anexou os handlers —, e como o ponteiro não se
   * move de novo, o `expect` seguinte espera cinco segundos por uma tooltip que
   * nunca vai abrir. Isso passava por sorte no Next 15 e quebrou quatro testes no
   * 16, todos os que fazem hover no primeiro paint em vez de depois de um clique.
   */
  await page.goto("/", { waitUntil: "networkidle" });
});

/**
 * Faz hover até a tooltip abrir, e devolve o conteúdo dela.
 *
 * Um `hover()` único é uma corrida perdida: se ele acontece antes da hidratação,
 * o Base UI não tem handler para receber o evento, e como o ponteiro não se move
 * de novo a tooltip nunca abre — o `expect` seguinte espera cinco segundos por
 * algo que já foi decidido. Passava por sorte no Next 15 e quebrou quatro testes
 * no 16. Esperar mais não resolve; repetir o HOVER resolve.
 */
async function tooltipOf(page: Page, target: Locator): Promise<Locator> {
  const tip = page.locator('[data-slot="tooltip-content"]');
  await expect(async () => {
    await page.mouse.move(2, 2);
    await target.hover();
    await expect(tip.first()).toBeVisible({ timeout: 1000 });
  }).toPass({ timeout: 15_000 });
  return tip.first();
}

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
  // Contagem por regex: ela cresce a cada varredura, e travar o número faria
  // este teste falhar por sucesso da pesquisa.
  await expect(page.getByText(/\d+ programas acompanhados/)).toBeVisible();
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
  // Base UI does not set role="tooltip" — the popup is identified by its slot.
  const tip = await tooltipOf(page, card(page, "CCO-724"));
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
  const tip = await tooltipOf(page, row.getByText("AMPLN"));
  await expect(tip).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  await expect(tip).toContainText("Ensinar computadores a aprender padrões");
  await expect(tip).toContainText("Docentes");
});

test("a line with no offering this term says so instead of showing nothing", async ({ page }) => {
  // BD taught nothing in 2026/2. An empty field would read as missing data;
  // the absence is itself the information.
  await openPpgcc(page);
  const row = page.getByRole("row", { name: /Banco de Dados/ });
  const tip = await tooltipOf(page, row.getByText("BD", { exact: true }));
  await expect(tip).toContainText("nenhuma disciplina ofertada");
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
  // .last(): "TOTI" passou a aparecer também no bloco de próximos passos, então
  // a linha da TABELA de linhas de pesquisa é a última ocorrência.
  const row = page.getByRole("row", { name: /TOTI/ }).last();
  const tip = await tooltipOf(page, row.getByText("TOTI", { exact: true }));
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

test("a manchete não afirma ser o único quando não é", async ({ page }) => {
  /**
   * O card dizia "É o único processo aberto que atende aos quatro requisitos", e
   * isso virou mentira no minuto em que o monitor achou o segundo edital. Manchete
   * que afirma exclusividade tem de ser derivada, não escrita.
   */
  const banner = page.locator("main > div").first();
  await expect(banner).toContainText("quatro requisitos verificados");
  await expect(banner).toContainText("Também aberto");
  await expect(banner).toContainText("PPGAdS");
  // O segundo tem o horário não verificado, e a página diz isso.
  await expect(banner).toContainText("horário a verificar");
});

test("o ciclo previsto do PPGCC aparece, com a previsão e sem datas falsas", async ({
  page,
}) => {
  /**
   * O PPGCC é o programa que o Victor mais quer, e não tem edital aberto. O que a
   * página precisa dizer é QUANDO esperar — e não pode inventar data para isso.
   *
   * Isto também guarda um bug real: `cycles.find(program === "PPGCC")` mostrava só
   * o primeiro ciclo, e no dia em que o previsto entrou o encerrado sumiu junto com
   * o aviso de rótulo contraditório.
   */
  await openPpgcc(page);

  const previsto = page.locator("div").filter({ hasText: /^PPGCC · Mestrado 2027\/1/ }).first();
  await expect(previsto).toContainText("previsto");
  await expect(previsto).toContainText("Edital ainda não publicado");
  await expect(previsto).toContainText("outubro de 2026");

  // E o encerrado continua ali, com o aviso.
  await expect(page.getByText(/O site ainda rotula este processo como/)).toBeVisible();
});

test("the options table shows every programme investigated, eliminated included", async ({
  page,
}) => {
  /**
   * "Já olhamos esse?" custa tanto quanto "qual serve?". A tabela existe para
   * que a varredura não seja refeita todo mês.
   */
  const table = page.locator("table").filter({ hasText: "Veredito" });
  for (const acronym of ["PPGPEP", "PPGCC", "PPGEE", "PIPGEs"]) {
    await expect(table.getByText(acronym, { exact: false }).first()).toBeVisible();
  }
  // Aprovado primeiro: a ordem da tabela é a ordem em que gastar atenção.
  const first = table.locator("tbody tr").first();
  await expect(first).toContainText("PPGPEP");
  await expect(first).toContainText("aprovado");
});

test("a verdict carries the evidence that produced it", async ({ page }) => {
  // Um veredito sem o porquê obriga a refazer a pesquisa a cada dúvida.
  const row = page.getByRole("row", { name: /PIPGEs/ });
  const tip = await tooltipOf(page, row.locator('[data-slot="tooltip-trigger"]').first());
  await expect(tip).toContainText("não atende");
  await expect(tip).toContainText("16:00–17:40");
});

test("an unverified requirement reads as pending work, never as a no", async ({ page }) => {
  const row = page.getByRole("row", { name: /PPGEE/ });
  // Terceiro requisito: gratuidade, não verificada porque o horário já eliminou.
  const tip = await tooltipOf(page, row.locator('[data-slot="tooltip-trigger"]').nth(2));
  await expect(tip).toContainText("não verificado");
});

test("the eliminated rows can be hidden without losing them", async ({ page }) => {
  // Contagens são derivadas da página, nunca fixas: a varredura cresce, e um
  // número literal aqui falharia por SUCESSO da pesquisa.
  const table = page.locator("table").filter({ hasText: "Veredito" });
  const total = await table.locator("tbody tr").count();
  expect(total).toBeGreaterThan(4);

  const hide = page.getByRole("button", { name: /Ocultar \d+ eliminados/ });
  const hidden = Number((await hide.textContent())!.match(/\d+/)![0]);
  await hide.click();

  await expect(table.locator("tbody tr")).toHaveCount(total - hidden);
  await expect(table.getByText("eliminado")).toHaveCount(0);

  await page.getByRole("button", { name: /Mostrando só viáveis/ }).click();
  await expect(table.locator("tbody tr")).toHaveCount(total);
});

test("the table filters by programme and by institution", async ({ page }) => {
  const table = page.locator("table").filter({ hasText: "Veredito" });
  await page.getByLabel("Filtrar opções").fill("PIPGEs");
  await expect(table.locator("tbody tr")).toHaveCount(1);
  await expect(table.locator("tbody tr")).toContainText("Estatística");
});

test("o índice de aderência mostra a cobertura junto do número", async ({ page }) => {
  /**
   * Um índice sobre dois sinais não é comparável a um sobre cinco. Mostrar só a
   * porcentagem convidaria exatamente a comparação errada.
   */
  const row = page.getByRole("row", { name: /PPGCTS/ });
  await expect(row).toContainText("%");
  await expect(row).toContainText("/5");
});

test("a aderência abre a evidência de cada um dos cinco sinais", async ({ page }) => {
  const row = page.getByRole("row", { name: /PPGCTS/ });
  // O último trigger da linha é o da coluna de aderência (os quatro primeiros
  // são os requisitos).
  const tip = await tooltipOf(page, row.locator('[data-slot="tooltip-trigger"]').last());
  await expect(tip).toContainText("Aderência ao trabalho na FAI");
  await expect(tip).toContainText("Restrições e governança");
  // "plausível" marca o que vem do escopo declarado e não de algo lido — a
  // distinção que evita repetir o erro da AMPLN.
  await expect(tip).toContainText("plausível");
});

test("o edital abre embutido, pela NOSSA origem", async ({ page }) => {
  /**
   * O iframe TEM que apontar para /api/notices/{id}/pdf. Os PDFs da UFSCar
   * respondem X-Frame-Options: SAMEORIGIN — apontar para a URL original deixa o
   * painel em branco sem nenhum erro visível.
   */
  const row = page.getByRole("row", { name: /PPGPEP/ }).first();
  await row.getByRole("button", { name: /001\/2026/ }).click();

  const dialog = page.getByRole("dialog");
  await expect(dialog).toContainText("Edital PPGPEP");
  await expect(dialog.getByRole("link", { name: /abrir na fonte/ })).toBeVisible();

  const frame = dialog.locator("iframe");
  const src = await frame.getAttribute("src");
  expect(src).toMatch(/^\/api\/notices\/\d+\/pdf$/);

  // E o PDF tem que responder de verdade, senão o painel abre vazio.
  const res = await page.request.get(src!);
  expect(res.ok()).toBe(true);
  expect(res.headers()["content-type"]).toContain("application/pdf");
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

/**
 * A aba de aluno especial existe porque o veredito dela é de outra natureza: os
 * quatro requisitos avaliam o programa, e esta porta muda o que conta como
 * aprovado sem mudar nada no programa.
 *
 * O que estes testes protegem é a INVERSÃO. A resposta intuitiva — "vou me
 * inscrever como aluno especial no PPGCC" — é a errada, e a certa é um programa
 * que a página classifica como não-aprovado no processo regular. Se um refactor
 * fizer os dois cartões dizerem a mesma coisa, ninguém percebe lendo o diff.
 */
test("special-student tab inverts the verdict only where evening classes exist", async ({
  page,
}) => {
  await page.getByRole("tab", { name: /Aluno especial/ }).click();

  // Sem projeto de pesquisa é o que a porta resolve; o horário é o que ela não
  // resolve. As duas metades têm de aparecer, senão a página promete demais.
  await expect(page.getByText(/mesmas disciplinas da mesma grade/)).toBeVisible();
  await expect(page.getByText(/uma disciplina.*que caiba/i).first()).toBeVisible();

  const ppgcc = page.locator('[data-slot="card"]', { hasText: "PPGCC · Aluno especial" });
  await expect(ppgcc.getByText("não resolve o horário")).toBeVisible();

  // A EESC-EP tem 3 faixas noturnas em 18 — reprovada para integralizar, viável
  // para uma disciplina. É a única porta que abre, e vem antes do PPGCC.
  const eesc = page.locator('[data-slot="card"]', { hasText: "EESC-EP · Aluno especial" });
  await expect(eesc.getByText("pode caber")).toBeVisible();
  await expect(eesc).toContainText("SEP5843");

  // Pelo TÍTULO, não pelo texto do cartão: `hasText` casa o conteúdo inteiro, e
  // ancorar com `$` nunca fecha num cartão que tem parágrafo e link depois.
  const titles = page.locator('[data-slot="card-title"]', { hasText: "· Aluno especial" });
  await expect(titles.first()).toContainText("EESC-EP");
});

test("does not claim RU access it never verified", async ({ page }) => {
  await page.getByRole("tab", { name: /Aluno especial/ }).click();
  const ru = page.getByText(/Restaurante universitário/);
  await expect(ru).toBeVisible();
  // "imagino que não" era o palpite dele, "provavelmente sim" é o meu. Nenhum dos
  // dois é dado, e a página tem de dizer isso em vez de escolher um.
  await expect(page.getByText(/palpite não é dado/)).toBeVisible();
});
