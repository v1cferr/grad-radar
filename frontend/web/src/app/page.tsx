import { getCycles, getOfferings, getPrograms, type Cycle } from "@/lib/api";
import { ScheduleGrid } from "./schedule-grid";

export const dynamic = "force-dynamic";

const CANDIDATE = "Victor";

const STATUS_LABEL: Record<string, { text: string; icon: string; color: string }> = {
  // Status always ships icon + label. Colour alone never carries the meaning —
  // on a light surface two of these four sit below 3:1 contrast by design.
  open: { text: "inscrições abertas", icon: "●", color: "var(--status-good)" },
  announced: { text: "edital publicado", icon: "◆", color: "var(--status-warning)" },
  in_progress: { text: "em andamento", icon: "◑", color: "var(--status-serious)" },
  concluded: { text: "encerrado", icon: "✕", color: "var(--status-critical)" },
  expected: { text: "previsto", icon: "◇", color: "var(--ink-muted)" },
};

const fmt = (d: string | null) =>
  d ? new Date(`${d}T12:00:00`).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" }) : "—";

function Tile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div
      className="rounded-lg border p-4"
      style={{ background: "var(--surface-raised)", borderColor: "var(--border)" }}
    >
      <div className="text-xs" style={{ color: "var(--ink-muted)" }}>
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums" style={{ color: "var(--ink)" }}>
        {value}
      </div>
      {hint && (
        <div className="mt-0.5 text-xs" style={{ color: "var(--ink-secondary)" }}>
          {hint}
        </div>
      )}
    </div>
  );
}

function CycleCard({ c }: { c: Cycle }) {
  const s = STATUS_LABEL[c.status] ?? STATUS_LABEL.expected;
  const mismatch = c.site_label && c.status === "concluded";
  return (
    <div
      className="rounded-lg border p-5"
      style={{ background: "var(--surface-raised)", borderColor: "var(--border)" }}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold">
          {c.program} · Mestrado {c.year}/{c.semester}
        </h3>
        <span className="flex items-center gap-1.5 text-sm" style={{ color: s.color }}>
          <span aria-hidden>{s.icon}</span>
          <span style={{ color: "var(--ink-secondary)" }}>{s.text}</span>
        </span>
      </div>

      <p className="mt-1 text-sm" style={{ color: "var(--ink-secondary)" }}>
        Inscrições {fmt(c.applications_open_on)} – {fmt(c.applications_close_on)} · {c.total_seats} vagas
      </p>

      {mismatch && (
        <p
          className="mt-3 rounded-md border px-3 py-2 text-xs"
          style={{
            borderColor: "var(--status-warning)",
            color: "var(--ink-secondary)",
            background: "color-mix(in oklab, var(--status-warning) 10%, var(--surface))",
          }}
        >
          <span aria-hidden>⚠ </span>
          O site ainda rotula este processo como <strong>{c.site_label}</strong>. O status acima vem das
          datas do edital, não do rótulo — é por isso que ele não anuncia uma oportunidade que já fechou.
        </p>
      )}

      <h4 className="mt-5 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--ink-muted)" }}>
        Cronograma
      </h4>
      <ol className="mt-2 space-y-2">
        {c.stages.map((st) => (
          <li key={st.ordinal} className="flex gap-3 text-sm">
            <span
              className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs tabular-nums"
              style={{ background: "var(--border)", color: "var(--ink-secondary)" }}
            >
              {st.ordinal}
            </span>
            <span>
              <span style={{ color: "var(--ink)" }}>{st.name}</span>
              <span style={{ color: "var(--ink-secondary)" }}>
                {" "}
                — {fmt(st.starts_on)} a {fmt(st.ends_on)}
                {st.result_on && `, resultado ${fmt(st.result_on)}`}
              </span>
            </span>
          </li>
        ))}
      </ol>

      <h4 className="mt-5 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--ink-muted)" }}>
        Vagas por linha
      </h4>
      <div className="mt-2 space-y-1.5">
        {c.seats.map((s2) => {
          const max = Math.max(...c.seats.map((x) => x.seats));
          return (
            <div key={s2.research_line ?? "?"} className="flex items-center gap-2 text-sm">
              <span className="w-16 shrink-0 text-xs" style={{ color: "var(--ink-secondary)" }}>
                {s2.research_line}
              </span>
              <span className="flex-1">
                <span
                  className="block h-2 rounded-sm"
                  style={{ width: `${(s2.seats / max) * 100}%`, background: "var(--cat-1)" }}
                />
              </span>
              <span className="w-6 text-right text-xs tabular-nums" style={{ color: "var(--ink)" }}>
                {s2.seats}
              </span>
            </div>
          );
        })}
      </div>

      <h4 className="mt-5 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--ink-muted)" }}>
        Documentos exigidos
      </h4>
      <ul className="mt-2 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-2" style={{ color: "var(--ink-secondary)" }}>
        {c.required_documents.map((d) => (
          <li key={d}>· {d}</li>
        ))}
      </ul>

      {c.official_url && (
        <a
          className="mt-5 inline-block text-sm underline underline-offset-2"
          href={c.official_url}
          style={{ color: "var(--cat-1)" }}
        >
          Página oficial do processo →
        </a>
      )}
    </div>
  );
}

export default async function Home() {
  const [programs, cycles, offerings] = await Promise.all([
    getPrograms(),
    getCycles(),
    getOfferings(CANDIDATE),
  ]);

  const program = programs[0];
  const conflicts = offerings.filter((o) => o.conflicts_with_work === true).length;
  const ampln = program?.research_lines.find((l) => l.acronym === "AMPLN");
  const amplnSeats = cycles[0]?.seats.find((s) => s.research_line === "AMPLN")?.seats;

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">GradRadar</h1>
        <p className="mt-1 text-sm" style={{ color: "var(--ink-secondary)" }}>
          {program ? `${program.name} · ${program.institution} ${program.campus}` : "sem dados"}
          {program?.capes_rating && ` · CAPES ${program.capes_rating}`}
        </p>
      </header>

      <section className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Tile label="Ofertas em 2026/2" value={String(offerings.length)} hint="grade publicada" />
        <Tile
          label="Conflitam com sua jornada"
          value={`${conflicts}/${offerings.length}`}
          hint="não há oferta noturna"
        />
        <Tile
          label="Docentes na AMPLN"
          value={String(ampln?.faculty_count ?? 0)}
          hint="a linha de IA/ML/PLN"
        />
        <Tile label="Vagas na AMPLN" value={String(amplnSeats ?? "—")} hint="último edital" />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Processos seletivos</h2>
        <div className="mt-3 space-y-4">
          {cycles.map((c) => (
            <CycleCard key={c.id} c={c} />
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Grade semanal · 2026/2</h2>
        <p className="mt-1 mb-4 text-sm" style={{ color: "var(--ink-secondary)" }}>
          O programa publica apenas duas faixas, e nenhuma é noturna.
        </p>
        <ScheduleGrid offerings={offerings} workLabel="08:00–18:00" />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Linhas de pesquisa</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ color: "var(--ink-muted)" }}>
                <th className="py-2 text-left font-medium">Sigla</th>
                <th className="py-2 text-left font-medium">Nome</th>
                <th className="py-2 text-right font-medium">Docentes</th>
              </tr>
            </thead>
            <tbody>
              {program?.research_lines.map((l) => (
                <tr key={l.id} className="border-t" style={{ borderColor: "var(--border)" }}>
                  <td className="py-2 font-mono text-xs">{l.acronym}</td>
                  <td className="py-2" style={{ color: "var(--ink-secondary)" }}>
                    {l.name}
                  </td>
                  <td className="py-2 text-right tabular-nums">{l.faculty_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="mt-12 text-xs" style={{ color: "var(--ink-muted)" }}>
        Dados verificados em fontes oficiais do PPGCC/UFSCar — ver docs/research/ufscar-ppgcc.md.
        Campos não afirmados pela fonte ficam vazios, nunca preenchidos por inferência.
      </footer>
    </main>
  );
}
