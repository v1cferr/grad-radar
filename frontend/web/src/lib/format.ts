/** Datas curtas em pt-BR. Meio-dia evita o deslocamento de fuso que faz
 *  `new Date("2026-08-20")` virar 19/08 em UTC-3. */
export const fmt = (d: string | null | undefined) =>
  d
    ? new Date(`${d}T12:00:00`).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })
    : "—";

export const fmtLong = (d: string | null | undefined) =>
  d
    ? new Date(`${d}T12:00:00`).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : "—";

export const daysUntil = (d: string | null | undefined, from: Date) =>
  d ? Math.ceil((new Date(`${d}T23:59:59`).getTime() - from.getTime()) / 86400000) : null;
