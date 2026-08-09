import {
  AlertTriangle,
  Ban,
  CalendarClock,
  CalendarX2,
  Clock,
  Info,
  Users,
} from "lucide-react";

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
  getSources,
  type Cycle,
  type ResearchLine,
} from "@/lib/api";

import { LineTooltip } from "./research-line";
import { Sources } from "./sources";
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
  // O PPGCC distribui vagas por linha; o PPGPEP explicitamente NÃO (edital 3.6).
  // Renderizar uma barra sem rótulo seria pior que dizer que a divisão não existe.
  const seatsByLine = c.seats.some((s2) => s2.research_line !== null);

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
                    {/* Nem toda etapa tem janela: a avaliação do projeto no PPGPEP
                        só publica a data do resultado. "— a —" fingiria uma lacuna
                        que não existe. */}
                    {st.starts_on && ` — ${fmt(st.starts_on)} a ${fmt(st.ends_on)}`}
                    {st.result_on &&
                      `${st.starts_on ? ", resultado " : " — resultado "}${fmt(st.result_on)}`}
                  </span>
                </span>
              </li>
            ))}
          </ol>
        </section>

        <Separator />

        <section>
          <h4 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            {seatsByLine ? "Vagas por linha" : "Vagas"}
          </h4>
          {!seatsByLine && (
            <p className="mt-3 text-sm text-muted-foreground">
              <strong className="text-foreground tabular-nums">{c.total_seats} vagas</strong> — o
              edital não as distribui por linha de pesquisa, então concorre-se a todas
              independentemente da linha escolhida.
            </p>
          )}
          <div className="mt-3 space-y-2">
            {(seatsByLine ? c.seats : []).map((s2) => (
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
  const [programs, cycles, offerings, sources] = await Promise.all([
    getPrograms(),
    getCycles(),
    getOfferings(CANDIDATE),
    getSources(),
  ]);

  // Nomeado explicitamente, nunca programs[0]: a ordem mudou no dia em que um
  // segundo programa entrou, e os números do PPGCC apareceram sob o título de
  // outro programa sem que nada quebrasse.
  const ppgcc = programs.find((p) => p.acronym === "PPGCC");
  const linesOf = (acronym: string) =>
    programs.find((p) => p.acronym === acronym)?.research_lines ?? [];
  const program = ppgcc;
  const conflicts = offerings.filter((o) => o.conflicts_with_work === true).length;
  const ampln = ppgcc?.research_lines.find((l) => l.acronym === "AMPLN");
  const amplnSeats = cycles
    .find((c) => c.program === "PPGCC")
    ?.seats.find((s) => s.research_line === "AMPLN")?.seats;

  // A única coisa desta página com prazo. Vem antes de tudo porque é a única que
  // é perdida por não ser vista a tempo.
  const today = new Date();
  const actionable = cycles
    .filter((c) => c.applications_close_on && new Date(`${c.applications_close_on}T23:59:59`) >= today)
    .sort((a, b) => (a.applications_close_on! < b.applications_close_on! ? -1 : 1))[0];
  const daysLeft = actionable
    ? Math.ceil(
        (new Date(`${actionable.applications_close_on}T23:59:59`).getTime() - today.getTime()) /
          86400000,
      )
    : null;
  const daysToOpen = actionable?.applications_open_on
    ? Math.ceil(
        (new Date(`${actionable.applications_open_on}T00:00:00`).getTime() - today.getTime()) /
          86400000,
      )
    : null;
  const eveningOfferings = offerings.filter((o) => o.starts_at && o.starts_at >= "18:00:00").length;

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">GradRadar</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Pós-graduação pública, gratuita, presencial em São Carlos e com aula à noite ·{" "}
          {programs.length} programas acompanhados
        </p>
      </header>

      {actionable && (
        <Card className="mt-6 border-2" style={{ borderColor: "var(--status-good)" }}>
          <CardContent className="flex flex-wrap items-start gap-4 px-6">
            <CalendarClock className="mt-0.5 size-5 shrink-0" style={{ color: "var(--status-good)" }} />
            <div className="min-w-0 flex-1 space-y-1">
              <p className="font-medium">
                {actionable.program} — inscrições {daysToOpen !== null && daysToOpen > 0 ? "abrem" : "abertas"}{" "}
                {fmt(actionable.applications_open_on)} a {fmt(actionable.applications_close_on)}
              </p>
              <p className="text-sm text-muted-foreground">
                É o único processo aberto que atende aos quatro requisitos: noturno, presencial em
                São Carlos, gratuito e público. A seleção é inteiramente sobre um{" "}
                <strong className="text-foreground">projeto de pesquisa</strong> — não há prova de
                conteúdo —, e ele precisa estar escrito antes de a inscrição abrir.
              </p>
            </div>
            <div className="shrink-0 text-right">
              <div className="text-3xl font-semibold tabular-nums">{daysLeft}</div>
              <div className="text-xs text-muted-foreground">
                {daysLeft === 1 ? "dia até fechar" : "dias até fechar"}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* The requirement is eliminatory, not a scoring dimension — so it is stated
          at the top, before any number that might suggest a trade-off exists. */}
      {eveningOfferings === 0 && (
        <Alert className="mt-6">
          <Ban className="size-4" />
          <AlertDescription>
            <strong>PPGCC eliminado: não há oferta noturna.</strong> Nenhuma das{" "}
            {offerings.length} disciplinas deste semestre começa depois das 18:00. Com jornada{" "}
            {WORK}, cursar este programa exigiria acordo com o empregador — não é questão de
            escolher a disciplina certa. Os números abaixo descrevem o programa eliminado; o
            processo com prazo é o do card acima.
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
            <CycleCard key={c.id} c={c} lines={linesOf(c.program)} />
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Grade semanal do PPGCC · 2026/2</h2>
        <p className="mt-1 mb-4 text-sm text-muted-foreground">
          O programa publica apenas duas faixas, e nenhuma é noturna. Passe o mouse numa disciplina
          para ver docente, créditos, salas e idioma.
        </p>
        <ScheduleGrid offerings={offerings} workLabel={WORK} lines={linesOf("PPGCC")} />
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Linhas de pesquisa do PPGCC</h2>
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

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Monitoramento</h2>
        <p className="mt-1 mb-4 text-sm text-muted-foreground">
          O coletor compara o TEXTO extraído, não os bytes — PDF regerado muda byte a byte dizendo a
          mesma coisa, e um monitor que grita à toa ninguém lê.
        </p>
        <Sources sources={sources} />
      </section>

      <footer className="mt-12 text-xs text-muted-foreground">
        Dados verificados em fontes oficiais da UFSCar — ver docs/research/. Campos não afirmados
        pela fonte ficam vazios, nunca preenchidos por inferência.
      </footer>
    </main>
  );
}
