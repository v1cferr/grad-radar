"use client";

import { CalendarClock, FileText, Send, UserRoundSearch } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Cycle, ResearchLine } from "@/lib/api";
import { daysUntil, fmt, fmtLong } from "@/lib/format";

import { LineTooltip } from "./research-line";

/**
 * O edital traduzido no que uma pessoa precisa FAZER, e quando.
 *
 * Um cronograma de dezenove linhas administrativas não responde "o que eu faço
 * agora" — e essa é a única pergunta que importa para quem tem quatro semanas.
 * As três primeiras etapas acontecem ANTES de a inscrição abrir, o que é
 * contraintuitivo e é justamente onde o prazo se perde.
 *
 * O que é do edital está marcado como tal. A ordem e a urgência são leitura
 * nossa, e ficam visualmente separadas — a mesma regra que vale para as glosas
 * das linhas de pesquisa.
 */
export function NextSteps({
  cycle,
  lines,
  today,
}: {
  cycle: Cycle;
  lines: ResearchLine[];
  today: Date;
}) {
  const opensIn = daysUntil(cycle.applications_open_on, today);
  const open = opensIn !== null && opensIn <= 0;

  const steps = [
    {
      id: "projeto",
      icon: FileText,
      title: "Escrever o projeto de pesquisa",
      when: `antes de ${fmt(cycle.applications_open_on)}`,
      urgent: true,
      body: (
        <>
          <p>
            É <strong>a única coisa avaliada</strong>. A etapa 1 dá nota ao projeto escrito e a
            etapa 2 é a defesa oral dele diante da comissão. Não há prova de conteúdo nem exame de
            proficiência eliminatório.
          </p>
          <p className="text-muted-foreground">
            Sem projeto pronto não há o que submeter em {fmt(cycle.applications_open_on)}, e a
            janela até lá é o prazo real — não {fmt(cycle.applications_close_on)}.
          </p>
        </>
      ),
    },
    {
      id: "orientador",
      icon: UserRoundSearch,
      title: "Falar com um docente e obter a declaração de vínculo",
      when: "antes de inscrever",
      urgent: true,
      body: (
        <>
          <p>
            O edital exige a declaração do <strong>Anexo II</strong>, assinada por um membro do
            corpo docente. Na prática isso significa conversar com um possível orientador antes da
            inscrição — e ninguém responde e-mail em um dia.
          </p>
          <div className="space-y-1.5">
            <p className="text-muted-foreground">As três linhas do programa:</p>
            <div className="flex flex-wrap gap-1.5">
              {lines.map((l) => (
                <LineTooltip key={l.acronym} line={l} termCollected={false} className="no-underline">
                  <Badge variant="outline" className="gap-1.5 font-normal">
                    <span
                      aria-hidden
                      className="size-2 rounded-full"
                      style={{ background: `var(--cat-${lines.indexOf(l) + 1})` }}
                    />
                    <span className="underline decoration-dotted underline-offset-2">
                      {l.acronym}
                    </span>
                  </Badge>
                </LineTooltip>
              ))}
            </div>
          </div>
        </>
      ),
    },
    {
      id: "documentos",
      icon: FileText,
      title: `Reunir os ${cycle.required_documents.length} documentos exigidos`,
      when: "antes de inscrever",
      urgent: false,
      body: (
        <ul className="grid gap-x-6 gap-y-1.5 sm:grid-cols-2">
          {cycle.required_documents.map((d) => (
            <li key={d} className="text-muted-foreground">
              · {d}
            </li>
          ))}
        </ul>
      ),
    },
    {
      id: "inscricao",
      icon: Send,
      title: "Fazer a inscrição",
      when: `${fmt(cycle.applications_open_on)} a ${fmt(cycle.applications_close_on)}`,
      urgent: open,
      body: (
        <>
          <p>
            Janela de {fmtLong(cycle.applications_open_on)} a{" "}
            {fmtLong(cycle.applications_close_on)}.
          </p>
          {cycle.official_url && (
            <a
              className="inline-block underline-offset-4 hover:underline"
              href={cycle.official_url}
              style={{ color: "var(--cat-1)" }}
            >
              Página oficial do processo seletivo →
            </a>
          )}
        </>
      ),
    },
  ];

  return (
    <Card>
      <CardContent className="px-6">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="font-medium">O que fazer, em ordem</h3>
          <p className="text-xs text-muted-foreground">
            {/* A distinção que este bloco existe para tornar óbvia. */}
            três das quatro etapas acontecem <strong>antes</strong> de a inscrição abrir
          </p>
        </div>

        <Accordion className="mt-2 -mb-2" defaultValue={["projeto"]}>
          {steps.map((s) => (
            <AccordionItem key={s.id} value={s.id}>
              <AccordionTrigger className="gap-3 text-left">
                <span className="flex min-w-0 flex-1 items-center gap-3">
                  <s.icon
                    className="size-4 shrink-0"
                    style={{ color: s.urgent ? "var(--status-warning)" : undefined }}
                    aria-hidden
                  />
                  <span className="min-w-0 flex-1">{s.title}</span>
                  <Badge variant={s.urgent ? "secondary" : "outline"} className="shrink-0 font-normal">
                    {s.when}
                  </Badge>
                </span>
              </AccordionTrigger>
              <AccordionContent className="space-y-2 pl-7 text-sm">{s.body}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}

/**
 * Onde o processo está agora, do edital ao resultado.
 *
 * Datas administrativas — recursos, listas preliminares, composição de comissão —
 * ficam de fora de propósito: elas não pedem ação de ninguém e afogariam as
 * cinco que pedem.
 */
export function Timeline({ cycle, today }: { cycle: Cycle; today: Date }) {
  const iso = today.toISOString().slice(0, 10);

  const points = [
    { label: "Inscrições", date: cycle.applications_open_on, end: cycle.applications_close_on },
    ...cycle.stages.map((s) => ({
      label: `Etapa ${s.ordinal}`,
      date: s.starts_on ?? s.result_on,
      end: s.result_on,
    })),
    { label: "Resultado", date: cycle.final_result_on, end: cycle.final_result_on },
  ].filter((p) => p.date);

  return (
    <div>
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <CalendarClock className="size-3.5" aria-hidden />
        Do edital ao resultado
      </div>

      <ol className="mt-3 grid gap-3 sm:grid-cols-4">
        {points.map((p) => {
          const done = p.end !== null && p.end < iso;
          const now = p.date! <= iso && !done;
          return (
            <li key={p.label} className="space-y-1.5">
              <div
                className="h-1 rounded-full"
                style={{
                  background: now
                    ? "var(--status-good)"
                    : done
                      ? "var(--muted-foreground)"
                      : "var(--border)",
                }}
              />
              <div className="text-xs font-medium">
                {p.label}
                {now && (
                  <span className="ml-1.5 font-normal" style={{ color: "var(--status-good)" }}>
                    · agora
                  </span>
                )}
              </div>
              <div className="text-xs text-muted-foreground tabular-nums">
                {fmt(p.date)}
                {p.end && p.end !== p.date && ` – ${fmt(p.end)}`}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
