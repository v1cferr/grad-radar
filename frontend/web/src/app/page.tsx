import { AlertTriangle, CalendarX2, Clock, Info, Ban, Users } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import {
  getCycles,
  getOfferings,
  getPrograms,
  type Cycle,
  type ResearchLine,
} from "@/lib/api";

import { LineTooltip } from "./research-line";
import { ScheduleGrid } from "./schedule-grid";

export const dynamic = "force-dynamic";

const CANDIDATE = "Victor";
const WORK = "08:00–18:00";

const STATUS: Record<string, { text: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  open: { text: "inscrições abertas", variant: "default" },
  announced: { text: "edital publicado", variant: "secondary" },
  in_progress: { text: "em andamento", variant: "secondary" },
  concluded: { text: "encerrado", variant: "outline" },
  expected: { text: "previsto", variant: "outline" },
};

const fmt = (d: string | null) =>
  d ? new Date(`${d}T12:00:00`).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" }) : "—";

function Tile({
  label,
  value,
  hint,
  icon: Icon,
  tooltip,
}: {
  label: string;
  value: string;
  hint: string;
  icon: React.ElementType;
  tooltip: string;
}) {
  return (
    <Tooltip>
      {/* Base UI merges props into the element given to `render`; there is no
          `asChild`. A div wrapper keeps the Card out of a <button>. */}
      <TooltipTrigger render={<div tabIndex={0} className="cursor-help" />}>
        <Card className="gap-0 py-4 transition-colors hover:bg-accent/40">
          <CardContent className="px-4">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Icon className="size-3.5" aria-hidden />
              {label}
            </div>
            <div className="mt-1.5 text-2xl font-semibold tabular-nums">{value}</div>
            <div className="text-xs text-muted-foreground">{hint}</div>
          </CardContent>
        </Card>
      </TooltipTrigger>
      <TooltipContent className="max-w-xs">{tooltip}</TooltipContent>
    </Tooltip>
  );
}

function CycleCard({ c, lines }: { c: Cycle; lines: ResearchLine[] }) {
  const s = STATUS[c.status] ?? STATUS.expected;
  const mismatch = c.site_label && c.status === "concluded";
  const maxSeats = Math.max(...c.seats.map((x) => x.seats), 1);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-base">
            {c.program} · Mestrado {c.year}/{c.semester}
          </CardTitle>
          <Badge variant={s.variant}>{s.text}</Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Inscrições {fmt(c.applications_open_on)} – {fmt(c.applications_close_on)} · {c.total_seats}{" "}
          vagas
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        {mismatch && (
          <Alert>
            <AlertTriangle className="size-4" />
            <AlertDescription>
              O site ainda rotula este processo como <strong>{c.site_label}</strong>. O status acima
              vem das datas do edital, não do rótulo — é por isso que ele não anuncia uma
              oportunidade que já fechou.
            </AlertDescription>
          </Alert>
        )}

        <section>
          <h4 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Cronograma
          </h4>
          <ol className="mt-3 space-y-3">
            {c.stages.map((st) => (
              <li key={st.ordinal} className="flex gap-3 text-sm">
                <Badge
                  variant="secondary"
                  className="size-5 shrink-0 justify-center rounded-full p-0 tabular-nums"
                >
                  {st.ordinal}
                </Badge>
                <span>
                  {st.name}
                  <span className="text-muted-foreground">
                    {" — "}
                    {fmt(st.starts_on)} a {fmt(st.ends_on)}
                    {st.result_on && `, resultado ${fmt(st.result_on)}`}
                  </span>
                </span>
              </li>
            ))}
          </ol>
        </section>

        <Separator />

        <section>
          <h4 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Vagas por linha
          </h4>
          <div className="mt-3 space-y-2">
            {c.seats.map((s2) => (
              <Tooltip key={s2.research_line ?? "?"}>
                <TooltipTrigger
                  render={<div className="flex cursor-help items-center gap-3 text-sm" />}
                >
                  <>
                    <LineTooltip
                      line={lines.find((l) => l.acronym === s2.research_line)}
                      className="w-14 shrink-0 font-mono text-xs text-muted-foreground"
                    >
                      {s2.research_line}
                    </LineTooltip>
                    <span className="flex-1">
                      <span
                        className="block h-2 rounded-sm"
                        style={{
                          width: `${(s2.seats / maxSeats) * 100}%`,
                          background: "var(--cat-1)",
                        }}
                      />
                    </span>
                    <span className="w-5 text-right text-xs tabular-nums">{s2.seats}</span>
                  </>
                </TooltipTrigger>
                <TooltipContent>
                  {s2.seats} {s2.seats === 1 ? "vaga" : "vagas"} em {s2.research_line} — de{" "}
                  {c.total_seats} no total
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        </section>

        <Separator />

        <section>
          <h4 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Documentos exigidos
          </h4>
          <ul className="mt-3 grid gap-x-6 gap-y-1.5 text-sm text-muted-foreground sm:grid-cols-2">
            {c.required_documents.map((d) => (
              <li key={d}>· {d}</li>
            ))}
          </ul>
        </section>

        {c.official_url && (
          <a
            className="inline-block text-sm underline-offset-4 hover:underline"
            href={c.official_url}
            style={{ color: "var(--cat-1)" }}
          >
            Página oficial do processo →
          </a>
        )}
      </CardContent>
    </Card>
  );
}

export default async function Home() {
  const [programs, cycles, offerings] = await Promise.all([
    getPrograms(),
    getCycles(),
    getOfferings(CANDIDATE),
  ]);

  const program = programs[0];
  const lines = program?.research_lines ?? [];
  const conflicts = offerings.filter((o) => o.conflicts_with_work === true).length;
  const ampln = program?.research_lines.find((l) => l.acronym === "AMPLN");
  const amplnSeats = cycles[0]?.seats.find((s) => s.research_line === "AMPLN")?.seats;
  const eveningOfferings = offerings.filter((o) => o.starts_at && o.starts_at >= "18:00:00").length;

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">GradRadar</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {program ? `${program.name} · ${program.institution} ${program.campus}` : "sem dados"}
          {program?.capes_rating != null && ` · CAPES ${program.capes_rating}`}
        </p>
      </header>

      {/* The requirement is eliminatory, not a scoring dimension — so it is stated
          at the top, before any number that might suggest a trade-off exists. */}
      {eveningOfferings === 0 && (
        <Alert className="mt-6">
          <Ban className="size-4" />
          <AlertDescription>
            <strong>Requisito não atendido: oferta noturna.</strong> Nenhuma das{" "}
            {offerings.length} disciplinas deste semestre começa depois das 18:00. Com jornada{" "}
            {WORK}, cursar este programa exigiria acordo com o empregador — não é questão de
            escolher a disciplina certa.
          </AlertDescription>
        </Alert>
      )}

      <section className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Tile
          label="Ofertas em 2026/2"
          value={String(offerings.length)}
          hint="grade publicada"
          icon={Info}
          tooltip="Disciplinas com oferta confirmada na grade oficial do semestre, extraída do PDF do SEI."
        />
        <Tile
          label="Conflitam com sua jornada"
          value={`${conflicts}/${offerings.length}`}
          hint="não há oferta noturna"
          icon={Clock}
          tooltip={`Calculado comparando cada faixa com ${WORK}. O programa publica apenas 08:00–12:00 e 14:00–18:00.`}
        />
        <Tile
          label="Docentes na AMPLN"
          value={String(ampln?.faculty_count ?? 0)}
          hint="a linha de IA/ML/PLN"
          icon={Users}
          tooltip="Aprendizado de Máquina e Processamento de Língua Natural — a única linha cujo nome cita IA diretamente."
        />
        <Tile
          label="Vagas na AMPLN"
          value={String(amplnSeats ?? "—")}
          hint="último edital"
          icon={CalendarX2}
          tooltip="Vagas alocadas especificamente à AMPLN no Edital 02/2026. Vagas são por linha, não um total do programa."
        />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Processos seletivos</h2>
        <div className="mt-4 space-y-4">
          {cycles.map((c) => (
            <CycleCard key={c.id} c={c} lines={lines} />
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Grade semanal · 2026/2</h2>
        <p className="mt-1 mb-4 text-sm text-muted-foreground">
          O programa publica apenas duas faixas, e nenhuma é noturna. Passe o mouse numa disciplina
          para ver docente, créditos, salas e idioma.
        </p>
        <ScheduleGrid offerings={offerings} workLabel={WORK} lines={lines} />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Linhas de pesquisa</h2>
        <Card className="mt-4 py-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-24">Sigla</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead className="text-right">Docentes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {program?.research_lines.map((l) => (
                <TableRow key={l.id}>
                  <TableCell className="font-mono text-xs">
                    <LineTooltip line={l}>{l.acronym}</LineTooltip>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{l.name}</TableCell>
                  <TableCell className="text-right tabular-nums">{l.faculty_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </section>

      <footer className="mt-12 text-xs text-muted-foreground">
        Dados verificados em fontes oficiais do PPGCC/UFSCar — ver docs/research/ufscar-ppgcc.md.
        Campos não afirmados pela fonte ficam vazios, nunca preenchidos por inferência.
      </footer>
    </main>
  );
}
