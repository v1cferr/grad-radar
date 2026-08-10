import type { Metadata } from "next";

/**
 * Identidade pública do site, num lugar só.
 *
 * Mora aqui e não no layout.tsx porque o robots.ts e a rota do og também
 * precisam dela, e importar do layout arrastaria o `next/font` para dentro de
 * rotas que devolvem texto e imagem.
 *
 * O default não é placeholder: é o domínio real, declarado em
 * dotfiles/system/services/caddy.nix. A variável de ambiente existe para que um
 * ambiente diferente (túnel, preview) não precise de mudança de código.
 */
export const SITE_URL = process.env.SITE_URL ?? "https://pos.v1cferr.dev";

export const SITE_NAME = "GradRadar";

export const SITE_DESCRIPTION =
  "Descobre, compara e acompanha processos seletivos de pós-graduação pública, " +
  "gratuita, presencial em São Carlos e com aula à noite — e avisa antes de o prazo fechar.";

/**
 * Dimensões da imagem de preview.
 *
 * Vivem aqui, e não na rota, porque a TAG e a IMAGEM têm que concordar: um
 * `og:image:width` que não bate com o PNG faz alguns clientes recortarem errado.
 * A rota importa esta mesma constante para gerar o PNG.
 */
export const OG_SIZE = { width: 1200, height: 630 };

/**
 * A imagem de preview, declarada explicitamente em vez de pela convenção de
 * arquivo `opengraph-image.tsx`.
 *
 * URL ABSOLUTA montada do SITE_URL: a convenção de arquivo emitia
 * `http://localhost:3000/opengraph-image` mesmo com `metadataBase` correto, e
 * como este deploy roda `next dev`, o crawler receberia um endereço que não
 * existe para ele. Ver o cabeçalho de app/og/route.tsx.
 */
export const OG_IMAGE = {
  url: `${SITE_URL}/og`,
  ...OG_SIZE,
  alt:
    "GradRadar — o processo seletivo aberto que atende aos quatro requisitos, " +
    "com o prazo de inscrição",
};

/**
 * Bases de openGraph/twitter para SPREAD em quem sobrescreve título e descrição.
 *
 * O merge de metadata do Next é RASO: um `openGraph` declarado na página
 * substitui o do layout INTEIRO em vez de completá-lo. Sem estas constantes,
 * definir só `openGraph.title` na página apagava `type`, `locale`, `siteName`,
 * `url` e a imagem — silenciosamente, porque nada quebra: as tags simplesmente
 * deixam de existir no HTML.
 *
 * Tipados e não `as const`: `as const` produz arrays `readonly`, que o tipo
 * `OGImage[]` do Next recusa.
 */
export const OG_BASE: NonNullable<Metadata["openGraph"]> = {
  type: "website",
  locale: "pt_BR",
  url: "/",
  siteName: SITE_NAME,
  images: [OG_IMAGE],
};

export const TWITTER_BASE: NonNullable<Metadata["twitter"]> = {
  // summary_large_image mesmo sem conta no X: o formato é lido por vários
  // clientes de chat como fallback quando o og deles falha.
  card: "summary_large_image",
  images: [OG_IMAGE],
};
