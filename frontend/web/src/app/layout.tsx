import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

import { TooltipProvider } from "@/components/ui/tooltip";
import { OG_BASE, SITE_DESCRIPTION, SITE_NAME, SITE_URL, TWITTER_BASE } from "@/lib/site";
import { cn } from "@/lib/utils";

import "./globals.css";

// `display: swap` so text is readable while the font loads; `variable` feeds
// --font-sans in globals.css, which is what Tailwind's font-sans resolves to.
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  // OBRIGATÓRIO para que `opengraph-image` vire URL absoluta. Sem ele o build
  // falha em qualquer campo de metadata com caminho relativo — e og:image
  // relativo é ignorado por todo crawler, então o preview sairia sem imagem.
  metadataBase: new URL(SITE_URL),

  title: {
    default: SITE_NAME,
    // Vale para segmentos FILHOS. Hoje há uma rota só; existe para que a
    // primeira página nova não nasça com título solto.
    template: `%s · ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  alternates: { canonical: "/" },

  // ── Por que noindex numa página pública ─────────────────────────────────
  // A página é aberta por conveniência: é assim que o link funciona sem login
  // para três pessoas. Isso não a torna algo que deva estar no Google — é a
  // busca de pós-graduação de pessoas específicas, e um resultado de pesquisa
  // sobreviveria ao projeto.
  //
  // Isto NÃO custa o preview do WhatsApp: WhatsApp, Telegram e Slack buscam a
  // URL diretamente e leem as tags OG. `noindex` é diretiva para índice de
  // BUSCA, não para quem renderiza preview. Dá para ter as duas coisas, e é o
  // que se quer aqui: rico no canal que usamos, invisível no que não usamos.
  robots: {
    index: false,
    follow: false,
    googleBot: { index: false, follow: false },
  },

  openGraph: {
    ...OG_BASE,
    title: "GradRadar — pós-graduação com aula à noite",
    description: SITE_DESCRIPTION,
    // A imagem vem de OG_BASE (lib/site.ts), com URL absoluta montada do
    // SITE_URL — ver o cabeçalho de app/og/route.tsx para por que a convenção
    // de arquivo não serve aqui.
  },

  twitter: {
    ...TWITTER_BASE,
    title: "GradRadar — pós-graduação com aula à noite",
    description: SITE_DESCRIPTION,
  },

  // Nada de telefone nem endereço na página; sem isto o Safari no iOS
  // transforma números soltos (datas, contagens de vagas) em links de ligação.
  formatDetection: { telephone: false, address: false, email: false },
};

export const viewport: Viewport = {
  // `themeColor` e `colorScheme` saíram de `metadata` no Next 14 — aqui é o
  // lugar atual. Dois valores porque a interface tem os dois temas: um só faria
  // a barra do navegador brigar com a página em metade dos casos.
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
  colorScheme: "light dark",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR" className={cn(inter.variable)} suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        {/* One provider at the root: every Tooltip below shares its timing, so
            hovering across cells feels continuous instead of re-arming.
            shadcn ships Base UI here, not Radix — the prop is `delay`. */}
        <TooltipProvider delay={150}>{children}</TooltipProvider>
      </body>
    </html>
  );
}
