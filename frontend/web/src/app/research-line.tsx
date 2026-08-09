"use client";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { ResearchLine } from "@/lib/api";

/** Fixed hue per line, shared with the weekly grid so the same acronym always
 *  wears the same colour. */
export const LINE_HUE: Record<string, string> = {
  AMPLN: "var(--cat-1)",
  BD: "var(--cat-2)",
  CCH: "var(--cat-3)",
  ES: "var(--cat-4)",
  SAR: "var(--cat-5)",
  SDARC: "var(--cat-6)",
  VC: "var(--cat-7)",
};

/**
 * An acronym nobody can be expected to know, with the explanation attached.
 *
 * Three layers, in order of authority: the official name (verified), how many
 * faculty the line has and what it actually taught this term (verified), and a
 * plain-language gloss that is OURS — the institution publishes names only. The
 * gloss is visually separated and labelled so it never reads as a quotation.
 */
export function LineTooltip({
  line,
  children,
  className,
}: {
  line: ResearchLine | undefined;
  children: React.ReactNode;
  className?: string;
}) {
  if (!line) return <>{children}</>;

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <span
            tabIndex={0}
            className={cn(
              "cursor-help underline decoration-dotted decoration-from-font underline-offset-4",
              "focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none",
              className,
            )}
          />
        }
      >
        {children}
      </TooltipTrigger>

      <TooltipContent className="max-w-sm">
        <div className="space-y-2">
          <div>
            <div className="flex items-center gap-1.5 font-medium">
              <span
                aria-hidden
                className="size-2 rounded-full"
                style={{ background: LINE_HUE[line.acronym] }}
              />
              {line.acronym}
            </div>
            <div className="text-[11px] opacity-80">{line.name}</div>
          </div>

          {line.description && (
            <p className="border-t pt-1.5 text-[11px] leading-relaxed opacity-90">
              {line.description}
            </p>
          )}

          <dl className="grid grid-cols-[auto_1fr] gap-x-2 gap-y-0.5 border-t pt-1.5 text-[11px]">
            <dt className="opacity-70">Docentes</dt>
            <dd>{line.faculty_count}</dd>
            <dt className="opacity-70">Em 2026/2</dt>
            <dd>
              {line.offerings.length > 0
                ? line.offerings.join(" · ")
                : "nenhuma disciplina ofertada"}
            </dd>
          </dl>
        </div>
      </TooltipContent>
    </Tooltip>
  );
}

/** The legend row under the weekly grid — every acronym explains itself. */
export function LineLegend({ lines }: { lines: ResearchLine[] }) {
  return (
    <>
      {lines.map((line) => (
        <LineTooltip key={line.acronym} line={line} className="no-underline">
          <span className="inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs">
            <span
              aria-hidden
              className="size-2 rounded-full"
              style={{ background: LINE_HUE[line.acronym] }}
            />
            <span className="underline decoration-dotted underline-offset-2">{line.acronym}</span>
          </span>
        </LineTooltip>
      ))}
    </>
  );
}
