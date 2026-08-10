import { expect, test } from "@playwright/test";

/**
 * Os metadados existem para um canal específico: o link vai por WhatsApp para o
 * JP e o César. Um preview quebrado não dá erro em lugar nenhum — a mensagem
 * simplesmente chega como URL crua, e ninguém abre.
 *
 * Por isso são testados: é o tipo de coisa que só se descobre errada quando
 * alguém já mandou o link.
 */

const attr = (name: string) =>
  `meta[property="${name}"], meta[name="${name}"]`;

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("o título e a descrição carregam o prazo real do edital", async ({ page }) => {
  await expect(page).toHaveTitle(/inscrições até .+ · GradRadar/);
  const description = page.locator(attr("description"));
  await expect(description).toHaveAttribute("content", /vagas/);
  await expect(description).toHaveAttribute("content", /projeto de pesquisa/);
});

test("a página fica fora de índice de busca", async ({ page }) => {
  /**
   * É pública por conveniência — sem login, para três pessoas. Isso não a torna
   * algo que deva estar no Google.
   */
  await expect(page.locator(attr("robots"))).toHaveAttribute(
    "content",
    /noindex/,
  );

  const robots = await page.request.get("/robots.txt");
  expect(robots.ok()).toBe(true);
  expect(await robots.text()).toContain("Disallow: /");
});

test("o og:image é URL ABSOLUTA e responde", async ({ page }) => {
  /**
   * O erro que este teste existe para pegar: a convenção `opengraph-image.tsx`
   * emitia `http://localhost:3000/...` mesmo com metadataBase correto, e o
   * crawler não alcança esse endereço. O preview sairia sem imagem, sem que
   * nada falhasse.
   */
  const image = page.locator(attr("og:image"));
  const url = await image.getAttribute("content");
  expect(url).toMatch(/^https?:\/\//);
  expect(url).not.toContain("localhost");

  // As dimensões declaradas têm que bater com o PNG servido, senão alguns
  // clientes recortam errado.
  await expect(page.locator(attr("og:image:width"))).toHaveAttribute("content", "1200");
  await expect(page.locator(attr("og:image:height"))).toHaveAttribute("content", "630");

  const res = await page.request.get("/og");
  expect(res.ok()).toBe(true);
  expect(res.headers()["content-type"]).toContain("image/png");
});

test("o openGraph do layout sobrevive à sobrescrita da página", async ({ page }) => {
  /**
   * O merge de metadata do Next é RASO: um `openGraph` parcial na página apaga o
   * do layout inteiro. Já apagou — type, locale, site_name e url desapareceram
   * sem que nada quebrasse.
   */
  await expect(page.locator(attr("og:type"))).toHaveAttribute("content", "website");
  await expect(page.locator(attr("og:locale"))).toHaveAttribute("content", "pt_BR");
  await expect(page.locator(attr("og:site_name"))).toHaveAttribute("content", "GradRadar");
  await expect(page.locator(attr("og:url"))).toHaveAttribute("content", /^https?:\/\//);
  await expect(page.locator(attr("twitter:card"))).toHaveAttribute(
    "content",
    "summary_large_image",
  );
});

test("o preview não promete um número de dias que vai envelhecer errado", async ({ page }) => {
  /**
   * Clientes de chat cacheiam o preview por tempo indeterminado. "Faltam 36
   * dias" entregue em outubro é uma afirmação falsa dita com confiança — por
   * isso título, descrição e imagem usam só a data absoluta.
   */
  const title = await page.title();
  const description = await page.locator(attr("description")).getAttribute("content");
  for (const text of [title, description ?? ""]) {
    expect(text).not.toMatch(/\d+\s*dias?/i);
  }
});

test("os ícones existem para aba e para tela inicial", async ({ page }) => {
  const icon = page.locator('link[rel="icon"]');
  await expect(icon).toHaveAttribute("type", "image/svg+xml");

  // O apple-touch-icon NÃO aceita SVG; sem um PNG o iOS usa um print da página.
  const apple = page.locator('link[rel="apple-touch-icon"]');
  await expect(apple).toHaveAttribute("sizes", "180x180");
  const res = await page.request.get((await apple.getAttribute("href"))!);
  expect(res.headers()["content-type"]).toContain("image/png");
});

test("o manifesto permite fixar na tela inicial", async ({ page }) => {
  // O uso real é no celular: o link chega por WhatsApp e abre no telefone.
  await expect(page.locator('link[rel="manifest"]')).toHaveCount(1);
  const res = await page.request.get("/manifest.webmanifest");
  const manifest = await res.json();
  expect(manifest.name).toContain("GradRadar");
  expect(manifest.display).toBe("standalone");
  expect(manifest.icons.length).toBeGreaterThan(0);
});

test("a cor da barra do navegador acompanha o tema", async ({ page }) => {
  await expect(page.locator('meta[name="theme-color"]')).toHaveCount(2);
});
