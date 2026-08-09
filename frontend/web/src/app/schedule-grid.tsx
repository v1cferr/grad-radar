"use client";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { Offering, ResearchLine, Weekday } from "@/lib/api";

import { LINE_HUE, LineLegend } from "./research-line";

const DAYS: { key: Weekday; label: string }[] = [
  { key: "monday", label: "Segunda" },
  { key: "tuesday", label: "Terça" },
  { key: "wednesday", label: "Quarta" },
  { key: "thursday", label: "Quinta" },
  { key: "friday", label: "Sexta" },
];

const hhmm = (t: string | null) => (t ? t.slice(0, 5) : "—");
const lang = (l: string | null) => (l === "en" ? "inglês" : l ? "português" : "—");

function Cell({ o }: { o: Offering }) {
  const line = o.research_line;
  const hue = line ? LINE_HUE[line] : "var(--muted-foreground)";

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <div
            tabIndex={0}
            className={cn(
              "cursor-help rounded-md border bg-card p-2 text-left text-xs",
              "transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
            )}
          />
        }
      >
        <div className="flex items-start gap-1.5">
          {/* The coloured mark carries identity; text stays in ink tokens. */}
          <span
            aria-hidden
            className="mt-1 size-2 shrink-0 rounded-full"
            style={{ background: hue }}
          />
          <div className="min-w-0">
            <div className="font-mono text-[11px] text-muted-foreground">{o.code}</div>
            <div className="leading-snug font-medium">{o.name}</div>
            <div className="mt-1 leading-snug text-muted-foreground">{o.professor}</div>
          </div>
        </div>
      </TooltipTrigger>

      <TooltipContent side="right" className="max-w-xs">
        <div className="space-y-1.5">
          <div>
            <div className="font-mono text-[11px] opacity-70">{o.code}</div>
            <div className="font-medium">{o.name}</div>
            {o.name_en && <div className="text-[11px] opacity-70 italic">{o.name_en}</div>}
          </div>
          <dl className="grid grid-cols-[auto_1fr] gap-x-2 gap-y-0.5 text-[11px]">
            <dt className="opacity-70">Docente</dt>
            <dd>{o.professor ?? "—"}</dd>
            <dt className="opacity-70">Linha</dt>
            <dd>{line ?? "Básica"}</dd>
            <dt className="opacity-70">Horário</dt>
            <dd>
              {hhmm(o.starts_at)}–{hhmm(o.ends_at)}
            </dd>
            <dt className="opacity-70">Créditos</dt>
            <dd>{o.credits ?? "—"}</dd>
            <dt className="opacity-70">Idioma</dt>
            <dd>{lang(o.language)}</dd>
            <dt className="opacity-70">Salas</dt>
            {/* Two rooms, because the same class runs at both campuses. */}
            <dd>{o.locations.join(" · ") || "—"}</dd>
          </dl>
          {o.conflicts_with_work && (
            <p className="border-t pt-1.5 text-[11px] opacity-80">
              Conflita integralmente com a jornada de 08:00–18:00.
            </p>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}

/**
 * The weekly grid, with the candidate's working day drawn as a band behind it.
 *
 * Showing a red badge per offering would state the conclusion without showing
 * the mechanism. Drawing the working day makes the finding legible at a glance:
 * every published slot falls inside it, because the programme has two bands and
 * neither is in the evening.
 */
export function ScheduleGrid({
  offerings,
  workLabel,
  lines,
}: {
  offerings: Offering[];
  workLabel: string;
  lines: ResearchLine[];
}) {
  const bands = [...new Set(offerings.map((o) => `${o.starts_at}|${o.ends_at}`))].sort();

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[56rem]">
        <div className="grid grid-cols-[5.5rem_repeat(5,1fr)] gap-2">
          <div />
          {DAYS.map((d) => (
            <div key={d.key} className="pb-1 text-xs font-semibold text-muted-foreground">
              {d.label}
            </div>
          ))}

          {bands.map((band) => {
            const [start, end] = band.split("|");
            return (
              <div key={band} className="contents">
                <div className="flex items-start gap-2 pt-2.5 font-mono text-xs text-muted-foreground">
                  {/* Solid edge marker: a low-opacity fill alone vanishes on dark. */}
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
                  const cells = offerings.filter(
                    (o) => o.weekday === d.key && o.starts_at === start,
                  );
                  return (
                    <div
                      key={d.key + band}
                      className="space-y-2 rounded-md border border-dashed p-1.5"
                      style={{
                        background: "color-mix(in oklab, var(--status-critical) 14%, transparent)",
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

        <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
          <span className="text-xs text-muted-foreground">
            Faixa sombreada = sua jornada ({workLabel})
          </span>
          <span className="text-muted-foreground/40">·</span>
          <LineLegend lines={lines} />
        </div>
      </div>
    </div>
  );
}
