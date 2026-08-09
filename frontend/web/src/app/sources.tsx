"use client";

import { AlertCircle, CheckCircle2, CircleDashed } from "lucide-react";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { Source } from "@/lib/api";

const rel = (iso: string | null) => {
  if (!iso) return "nunca";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "agora";
  if (mins < 60) return `há ${mins} min`;
  const h = Math.round(mins / 60);
  if (h < 24) return `há ${h}h`;
  return `há ${Math.round(h / 24)}d`;
};

const KIND: Record<string, string> = {
  graduate_program_page: "página do programa",
  admission_page: "processo seletivo",
  faculty_page: "docentes",
  course_catalog: "catálogo",
  schedule_pdf: "grade horária (PDF)",
  edital_pdf: "edital (PDF)",
  regulation_pdf: "regimento (PDF)",
};

/**
 * What the monitor watches and what it last saw.
 *
 * Failures are shown, never hidden. A source that quietly stops being reachable
 * is exactly how a deadline gets missed — the silence looks identical to "no
 * news", which is the failure mode this whole project exists to prevent.
 */
export function Sources({ sources }: { sources: Source[] }) {
  const failing = sources.filter((s) => s.last_error);
  const changed = sources.filter((s) => s.last_change_at);

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        {sources.length} fontes oficiais monitoradas ·{" "}
        {changed.length === 0 ? "nenhuma mudança detectada" : `${changed.length} com mudança`}
        {failing.length > 0 && ` · ${failing.length} inacessível(is)`}
      </p>

      <ul className="divide-y rounded-lg border">
        {sources.map((s) => {
          const state = s.last_error
            ? { Icon: AlertCircle, color: "var(--status-critical)", label: "falhou" }
            : s.last_change_at
              ? { Icon: CircleDashed, color: "var(--status-warning)", label: "mudou" }
              : { Icon: CheckCircle2, color: "var(--status-good)", label: "sem mudança" };

          return (
            <li key={s.id} className="flex items-center gap-3 px-3 py-2 text-sm">
              <Tooltip>
                <TooltipTrigger render={<span className="cursor-help" tabIndex={0} />}>
                  <state.Icon className="size-4 shrink-0" style={{ color: state.color }} />
                </TooltipTrigger>
                <TooltipContent className="max-w-sm">
                  <div className="space-y-1 text-[11px]">
                    <div className="font-medium">{state.label}</div>
                    <div className="opacity-80 break-all">{s.url}</div>
                    {s.redirects_to && (
                      <div className="border-t pt-1 opacity-80">
                        Redireciona para o SEI — o conteúdo real é um PDF, não a página.
                      </div>
                    )}
                    {s.last_error && (
                      <div className="border-t pt-1 opacity-80">{s.last_error}</div>
                    )}
                    <div className="border-t pt-1 opacity-70">
                      {s.checks} verificação(ões) · HTTP {s.last_status ?? "—"}
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>

              <span className="min-w-0 flex-1 truncate">{s.title ?? s.url}</span>
              <span className="hidden shrink-0 text-xs text-muted-foreground sm:inline">
                {KIND[s.source_type] ?? s.source_type}
              </span>
              <span className="w-20 shrink-0 text-right text-xs text-muted-foreground tabular-nums">
                {rel(s.last_checked_at)}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
