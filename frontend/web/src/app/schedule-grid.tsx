import type { Offering, Weekday } from "@/lib/api";

const DAYS: { key: Weekday; label: string }[] = [
  { key: "monday", label: "Segunda" },
  { key: "tuesday", label: "Terça" },
  { key: "wednesday", label: "Quarta" },
  { key: "thursday", label: "Quinta" },
  { key: "friday", label: "Sexta" },
];

/** Fixed hue per research line. Assigned by position and never cycled, so a line
 *  keeps its colour regardless of what is filtered out. */
const LINE_HUE: Record<string, string> = {
  AMPLN: "var(--cat-1)",
  BD: "var(--cat-2)",
  CCH: "var(--cat-3)",
  ES: "var(--cat-4)",
  SAR: "var(--cat-5)",
  SDARC: "var(--cat-6)",
  VC: "var(--cat-7)",
};

const hhmm = (t: string | null) => (t ? t.slice(0, 5) : "—");

function Cell({ o }: { o: Offering }) {
  const line = o.research_line;
  const hue = line ? LINE_HUE[line] : "var(--ink-muted)";
  return (
    <div
      className="rounded-md border p-2 text-xs"
      style={{ background: "var(--surface-raised)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start gap-1.5">
        {/* The coloured mark carries identity; the text stays in ink tokens. */}
        <span aria-hidden className="mt-1 h-2 w-2 shrink-0 rounded-full" style={{ background: hue }} />
        <div className="min-w-0">
          <div className="font-mono text-[11px]" style={{ color: "var(--ink-muted)" }}>
            {o.code}
          </div>
          <div className="font-medium leading-snug" style={{ color: "var(--ink)" }}>
            {o.name}
          </div>
          <div className="mt-1 leading-snug" style={{ color: "var(--ink-secondary)" }}>
            {o.professor}
          </div>
          <div className="mt-1 flex flex-wrap gap-x-2" style={{ color: "var(--ink-muted)" }}>
            <span>{line ?? "Básica"}</span>
            <span>{o.language === "en" ? "inglês" : "português"}</span>
            {o.locations[0] && <span>{o.locations[0]}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * The weekly grid, with the candidate's working day drawn as a band behind it.
 *
 * Showing 13 red "conflict" badges would state the conclusion without showing
 * the mechanism. Drawing the working day makes the real finding legible at a
 * glance: every published slot falls inside it, because the programme has only
 * two bands and neither is in the evening.
 */
export function ScheduleGrid({
  offerings,
  workLabel,
}: {
  offerings: Offering[];
  workLabel: string;
}) {
  const bands = [...new Set(offerings.map((o) => `${o.starts_at}|${o.ends_at}`))].sort();

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[52rem]">
        <div
          className="mb-3 flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs"
          style={{
            borderColor: "var(--status-critical)",
            color: "var(--ink-secondary)",
            background: "color-mix(in oklab, var(--status-critical) 8%, var(--surface))",
          }}
        >
          <span aria-hidden>▮</span>
          <span>Faixa sombreada = sua jornada ({workLabel}). Toda a grade cai dentro dela.</span>
        </div>

        <div className="grid grid-cols-[5rem_repeat(5,1fr)] gap-2">
          <div />
          {DAYS.map((d) => (
            <div key={d.key} className="pb-1 text-xs font-semibold" style={{ color: "var(--ink-secondary)" }}>
              {d.label}
            </div>
          ))}

          {bands.map((band) => {
            const [start, end] = band.split("|");
            return (
              <div key={band} className="contents">
                <div
                  className="flex items-start gap-2 pt-2 font-mono text-xs"
                  style={{ color: "var(--ink-secondary)" }}
                >
                  {/* The band is the argument, so it gets a solid edge marker as
                      well as a fill — a 7% tint alone disappears on dark. */}
                  <span
                    aria-hidden
                    className="mt-0.5 h-4 w-1 rounded-full"
                    style={{ background: "var(--status-critical)" }}
                  />
                  <span>
                    {hhmm(start)}–{hhmm(end)}
                  </span>
                </div>
                {DAYS.map((d) => {
                  const cells = offerings.filter((o) => o.weekday === d.key && o.starts_at === start);
                  return (
                    <div
                      key={d.key + band}
                      className="space-y-2 rounded-md border border-dashed p-1.5"
                      style={{
                        background: "color-mix(in oklab, var(--status-critical) 16%, transparent)",
                        borderColor: "color-mix(in oklab, var(--status-critical) 45%, transparent)",
                      }}
                    >
                      {cells.map((o) => (
                        <Cell key={o.id} o={o} />
                      ))}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>

        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs">
          {Object.entries(LINE_HUE).map(([acronym, hue]) => (
            <span key={acronym} className="flex items-center gap-1.5">
              <span aria-hidden className="h-2 w-2 rounded-full" style={{ background: hue }} />
              <span style={{ color: "var(--ink-secondary)" }}>{acronym}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
