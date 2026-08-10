import { ImageResponse } from "next/og";

import type { Option } from "@/lib/api";
import { OG_SIZE } from "@/lib/site";

/**
 * O preview do link — o que o JP e o César veem no WhatsApp antes de abrir.
 *
 * É um Route Handler e NÃO o arquivo `opengraph-image.tsx` de propósito. A
 * convenção de arquivo resolve a própria URL contra a origem do servidor de
 * desenvolvimento — emitia `http://localhost:3000/opengraph-image` mesmo com
 * `metadataBase` correto (o `og:url` ao lado saía certo). Como este projeto roda
 * `next dev` em produção, o crawler receberia um endereço que não existe para
 * ele, e o link sairia sem preview nenhum. Pior: a convenção de arquivo tem
 * PRIORIDADE sobre o objeto `metadata`, então declarar a URL absoluta por cima
 * não corrigia — era preciso tirar a convenção do caminho.
 *
 * Com a rota explícita, quem monta a tag é o layout, a partir do SITE_URL.
 *
 * NÃO MOSTRA CONTAGEM DE DIAS, e isso é deliberado. WhatsApp, Telegram e Slack
 * cacheiam o preview por URL, agressivamente e por tempo indeterminado. Um
 * "faltam 36 dias" renderizado hoje continuaria sendo entregue em outubro,
 * dizendo com confiança um número errado. A data absoluta — "até 14 de setembro
 * de 2026" — é verdadeira em qualquer momento que for lida.
 *
 * É a mesma regra que vale no resto do projeto: preferir o campo que não pode
 * envelhecer errado. Um prazo errado é pior que prazo nenhum, porque parece
 * informação.
 */
// O prazo muda; a imagem tem que mudar com ele. `force-dynamic` porque o
// default de um Route Handler é cache estático, e um preview congelado no dia
// do build mostraria o edital anterior.
export const dynamic = "force-dynamic";

const BASE = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";

const REQUIREMENTS = ["Aula à noite", "Presencial em São Carlos", "Gratuito", "Público"];

const longDate = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

async function openOption(): Promise<Option | null> {
  try {
    // no-store: o preview tem que refletir o edital de hoje, não o do build.
    const res = await fetch(`${BASE}/api/options`, { cache: "no-store" });
    if (!res.ok) return null;
    const options: Option[] = await res.json();
    return options.find((o) => o.verdict === "approved" && o.days_left !== null) ?? null;
  } catch {
    // O preview nunca pode ser o motivo de um erro: se a API não responde, a
    // imagem sai sem o bloco de prazo em vez de o link ficar sem preview.
    return null;
  }
}

export async function GET() {
  const option = await openOption();

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background: "#ffffff",
          fontFamily: "sans-serif",
        }}
      >
        {/* Faixa de acento à esquerda: dá identidade sem depender de logo, e
            sobrevive ao recorte quadrado que alguns clientes aplicam. */}
        <div style={{ width: 20, height: "100%", background: "#2a78d6", display: "flex" }} />

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "64px 72px",
            flex: 1,
          }}
        >
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", alignItems: "center" }}>
              <svg width="46" height="46" viewBox="0 0 32 32">
                <rect width="32" height="32" rx="7" fill="#2a78d6" />
                <g fill="none" stroke="#ffffff" strokeWidth="2.6" strokeLinecap="round">
                  <path d="M16 26.5A10.5 10.5 0 1 1 26.5 16" />
                  <path d="M16 16 23.4 8.6" />
                </g>
                <circle cx="23.5" cy="22.5" r="3.1" fill="#ffffff" />
              </svg>
              <div
                style={{
                  marginLeft: 16,
                  fontSize: 30,
                  fontWeight: 600,
                  color: "#0a0a0a",
                  display: "flex",
                }}
              >
                GradRadar
              </div>
            </div>

            {option ? (
              <div style={{ display: "flex", flexDirection: "column", marginTop: 40 }}>
                <div style={{ fontSize: 62, fontWeight: 700, color: "#0a0a0a", display: "flex" }}>
                  {option.acronym} · inscrições abertas
                </div>
                <div style={{ fontSize: 42, color: "#2a78d6", marginTop: 12, display: "flex" }}>
                  até {longDate(option.applications_close_on!)}
                </div>
                <div style={{ fontSize: 27, color: "#525252", marginTop: 20, display: "flex" }}>
                  {option.total_seats} vagas · {option.institution} {option.campus} · a seleção é um
                  projeto de pesquisa
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", marginTop: 40 }}>
                <div style={{ fontSize: 56, fontWeight: 700, color: "#0a0a0a", display: "flex" }}>
                  Pós-graduação com aula à noite
                </div>
                <div style={{ fontSize: 29, color: "#525252", marginTop: 20, display: "flex" }}>
                  Nenhum processo aberto agora. O monitor avisa quando abrir.
                </div>
              </div>
            )}
          </div>

          {/* Os quatro requisitos eliminatórios: dizem, sem texto corrido, por
              que este link existe. */}
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {REQUIREMENTS.map((r) => (
              <div
                key={r}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginRight: 34,
                  fontSize: 25,
                  color: "#404040",
                }}
              >
                <svg width="22" height="22" viewBox="0 0 24 24" style={{ marginRight: 9 }}>
                  <path
                    d="M4 12.5 9.5 18 20 6.5"
                    fill="none"
                    stroke="#0ca30c"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {r}
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
    { ...OG_SIZE },
  );
}
