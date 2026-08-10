import type { Metadata } from "next";
import {
  AlertTriangle,
  Ban,
  CalendarClock,
  CalendarX2,
  Check,
  Clock,
  ExternalLink,
  Info,
  Users,
  X,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import {
  getCycles,
  getOfferings,
  getOptions,
  getPrograms,
  getSources,
  type Cycle,
  type Program,
  type ResearchLine,
} from "@/lib/api";
import { daysUntil, fmt, fmtLong } from "@/lib/format";
import { OG_BASE, SITE_DESCRIPTION, SITE_NAME, TWITTER_BASE } from "@/lib/site";

import { NextSteps, Timeline } from "./next-steps";
import { OptionsTable } from "./options-table";
import { LineTooltip } from "./research-line";
import { ScheduleGrid } from "./schedule-grid";
import { Sources } from "./sources";

export const dynamic = "force-dynamic";

/**
 * Título e descrição seguem o edital, não um texto fixo.
 *
 * Pela MESMA razão da imagem de OG, aqui também não entra contagem de dias:
 * clientes de chat cacheiam o preview inteiro — título, descrição e imagem —, e
 * um "faltam 36 dias" congelado em outubro é uma afirmação falsa entregue com
 * confiança. A data absoluta não envelhece errado.
 */
export async function generateMetadata(): Promise<Metadata> {
  const cycles = await getCycles();
  const today = new Date().toISOString().slice(0, 10);
  const open = cycles
    .filter((c) => c.applications_close_on && c.applications_close_on >= today)
    .sort((a, b) => (a.applications_close_on! < b.applications_close_on! ? -1 : 1))[0];

  if (!open) {
    return {
      title: { absolute: `${SITE_NAME} — nenhum processo aberto` },
      description: `Nenhum processo seletivo aberto atende aos quatro requisitos. ${SITE_DESCRIPTION}`,
    };
  }

  const headline = `${open.program} — inscrições até ${fmtLong(open.applications_close_on)}`;
  const description =
    `${open.total_seats} vagas. A seleção é inteiramente um projeto de pesquisa, ` +
    `que precisa estar escrito antes de a inscrição abrir em ` +
    `${fmtLong(open.applications_open_on)}.`;

  return {
    title: { absolute: `${headline} · ${SITE_NAME}` },
    description,
    // Spread obrigatório: o merge do Next é raso, e um `openGraph` parcial aqui
    // apagaria type/locale/siteName/url declarados no layout.
    openGraph: { ...OG_BASE, title: headline, description },
    twitter: { ...TWITTER_BASE, title: headline, description },
  };
}

// ⚠️ ESTE É O LIMITE DA PÁGINA SEM LOGIN. Hoje o candidato só serve para calcular
// conflito de horário contra 08–18, que é público (docs/GOAL.md). No momento em
// que algo AQUI passar a ser sobre uma PESSOA e não sobre um PROGRAMA — anotação
// pessoal, ranking de preferência, rascunho de projeto, conversa com orientador —,
// a página deixa de poder ser aberta. Ver docs/SEM-LOGIN.md antes de adicionar.
const CANDIDATE = "Victor";
const WORK = "08:00–18:00";

const STATUS: Record<
  string,
  { text: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  open: { text: "inscrições abertas", variant: "default" },
  announced: { text: "edital publicado", variant: "secondary" },
  in_progress: { text: "em andamento", variant: "secondary" },
  concluded: { text: "encerrado", variant: "outline" },
  expected: { text: "previsto", variant: "outline" },
};

/** Os quatro requisitos do GOAL.md, na ordem em que eliminam. */
const REQUIREMENTS = [
  { label: "Aula à noite", why: "os três trabalham 08–18" },
  { label: "Presencial em São Carlos", why: "mudar de cidade não está em questão" },
  { label: "Gratuito", why: "sem mensalidade" },
  { label: "Público", why: "universidade pública" },
];

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

/** Por que este programa entra ou sai — os quatro requisitos, um a um. */
function Eligibility({ passes, failedOn }: { passes: boolean; failedOn?: number }) {
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-2 text-sm">
      {REQUIREMENTS.map((r, i) => {
        const failed = !passes && failedOn === i;
        return (
          <Tooltip key={r.label}>
            <TooltipTrigger render={<li tabIndex={0} className="flex cursor-help items-center gap-1.5" />}>
              <>
                {failed ? (
                  <X className="size-4 shrink-0" style={{ color: "var(--status-critical)" }} />
                ) : (
                  <Check className="size-4 shrink-0" style={{ color: "var(--status-good)" }} />
                )}
                <span className={failed ? "font-medium" : "text-muted-foreground"}>{r.label}</span>
              </>
            </TooltipTrigger>
            <TooltipContent>
              {failed ? "Requisito NÃO atendido — " : "Requisito atendido — "}
              {r.why}
            </TooltipContent>
          </Tooltip>
        );
      })}
    </ul>
  );
}

function CycleCard({
  c,
  lines,
  showSchedule = true,
  showDocuments = true,
}: {
  c: Cycle;
  lines: ResearchLine[];
  showSchedule?: boolean;
  showDocuments?: boolean;
}) {
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
          {/* Ciclo previsto não tem datas. "— a —" fingiria uma lacuna de dado
              quando o fato é que o edital ainda não saiu. */}
          {c.applications_open_on
            ? `Inscrições ${fmt(c.applications_open_on)} – ${fmt(c.applications_close_on)} · ${c.total_seats} vagas`
            : "Edital ainda não publicado"}
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

        {c.notes && !c.applications_open_on && (
          <Alert>
            <CalendarClock className="size-4" />
            <AlertDescription>{c.notes}</AlertDescription>
          </Alert>
        )}

        {showSchedule && c.stages.length > 0 && (
          <>
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
          </>
        )}

        {c.seats.length > 0 && (
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
        )}

        {showDocuments && c.required_documents.length > 0 && (
          <>
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
          </>
        )}

        {c.official_url && (
          <a
            className="inline-flex items-center gap-1.5 text-sm underline-offset-4 hover:underline"
            href={c.official_url}
            style={{ color: "var(--cat-1)" }}
          >
            Página oficial do processo <ExternalLink className="size-3.5" aria-hidden />
          </a>
        )}
      </CardContent>
    </Card>
  );
}

function LinesTable({
  program,
  termCollected,
}: {
  program: Program | undefined;
  termCollected: boolean;
}) {
  return (
    <Card className="py-0">
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
                <LineTooltip line={l} termCollected={termCollected}>
                  {l.acronym}
                </LineTooltip>
              </TableCell>
              <TableCell className="text-muted-foreground">{l.name}</TableCell>
              <TableCell className="text-right tabular-nums">
                {l.faculty_count > 0 ? l.faculty_count : "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

export default async function Home() {
  const [programs, cycles, offerings, sources, options] = await Promise.all([
    getPrograms(),
    getCycles(),
    getOfferings(CANDIDATE),
    getSources(),
    getOptions(),
  ]);

  // Nomeado explicitamente, nunca programs[0]: a ordem mudou no dia em que um
  // segundo programa entrou, e os números do PPGCC apareceram sob o título de
  // outro programa sem que nada quebrasse.
  const ppgcc = programs.find((p) => p.acronym === "PPGCC");
  const ppgpep = programs.find((p) => p.acronym === "PPGPEP");
  const linesOf = (acronym: string) =>
    programs.find((p) => p.acronym === acronym)?.research_lines ?? [];
  /**
   * TODOS os ciclos de um programa, na ordem em que merecem atenção.
   *
   * Era `find`, que devolvia o primeiro — e quebrou no dia em que o PPGCC ganhou
   * um segundo ciclo: a aba passou a mostrar o previsto de 2027/1 e sumiu com o
   * encerrado de 2026/2, junto com o aviso de rótulo contraditório. Um programa
   * tem vários ciclos por definição; escolher um deles é sempre uma decisão, e
   * `find` a tomava por acidente.
   */
  const RANK = { open: 0, announced: 1, in_progress: 2, expected: 3, concluded: 4 };
  const cyclesOf = (acronym: string) =>
    cycles
      .filter((c) => c.program === acronym)
      .sort(
        (a, b) =>
          (RANK[a.status as keyof typeof RANK] ?? 9) - (RANK[b.status as keyof typeof RANK] ?? 9) ||
          b.year - a.year,
      );

  const conflicts = offerings.filter((o) => o.conflicts_with_work === true).length;
  const ampln = ppgcc?.research_lines.find((l) => l.acronym === "AMPLN");
  const amplnSeats = cycles
    .find((c) => c.program === "PPGCC" && c.year === 2026 && c.semester === 2)
    ?.seats.find((s) => s.research_line === "AMPLN")?.seats;
  const eveningOfferings = offerings.filter((o) => o.starts_at && o.starts_at >= "18:00:00").length;

  // A única coisa desta página com prazo. Vem antes de tudo porque é a única que
  // é perdida por não ser vista a tempo.
  const today = new Date();
  const iso = today.toISOString().slice(0, 10);
  // Todos os processos que ainda dá para fazer, do prazo mais curto ao mais longo.
  // Era `[0]` direto, e a manchete afirmava "o único processo aberto" — virou
  // mentira no minuto em que o monitor achou o segundo.
  const openCycles = cycles
    .filter((c) => c.applications_close_on && c.applications_close_on >= iso)
    .sort((a, b) => (a.applications_close_on! < b.applications_close_on! ? -1 : 1));
  const actionable = openCycles[0];
  const others = openCycles.slice(1);
  // "Verificado" significa os quatro requisitos com evidência lida, não apenas
  // ausência de impedimento. Só isso justifica a palavra na manchete.
  const verified = (acronym: string) =>
    options.find((o) => o.acronym === acronym)?.verdict === "approved";
  const daysLeft = daysUntil(actionable?.applications_close_on, today);
  const daysToOpen = daysUntil(actionable?.applications_open_on, today);
  const ppgpepCycle = cyclesOf("PPGPEP")[0];

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
            <CalendarClock
              className="mt-0.5 size-5 shrink-0"
              style={{ color: "var(--status-good)" }}
            />
            <div className="min-w-0 flex-1 space-y-1">
              <p className="font-medium">
                {actionable.program} — inscrições{" "}
                {daysToOpen !== null && daysToOpen > 0 ? "abrem" : "abertas"}{" "}
                {fmtLong(actionable.applications_open_on)} a{" "}
                {fmtLong(actionable.applications_close_on)}
              </p>
              <p className="text-sm text-muted-foreground">
                {verified(actionable.program)
                  ? "É o único processo aberto com os quatro requisitos verificados. "
                  : "Processo aberto, com o requisito de horário ainda não verificado. "}
                A seleção é inteiramente sobre um{" "}
                <strong className="text-foreground">projeto de pesquisa</strong> — não há prova de
                conteúdo —, e ele precisa estar escrito antes de a inscrição abrir.
              </p>
              {others.length > 0 && (
                <p className="text-sm text-muted-foreground">
                  Também aberto:{" "}
                  {others.map((c, i) => (
                    <span key={c.id}>
                      {i > 0 && " · "}
                      <strong className="text-foreground">{c.program}</strong> até{" "}
                      {fmtLong(c.applications_close_on)}
                      {!verified(c.program) && " (horário a verificar)"}
                    </span>
                  ))}
                </p>
              )}
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

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Opções</h2>
        <p className="mt-1 mb-4 text-sm text-muted-foreground">
          Todos os programas já investigados, com os quatro requisitos eliminatórios lado a lado.
          Os eliminados continuam aqui — saber que um programa já foi olhado evita refazer a
          varredura, e a evidência da eliminação fica a um hover de distância.
        </p>
        <OptionsTable options={options} />
      </section>

      {/* Um programa aprovado e um eliminado não são duas seções de uma lista:
          são respostas opostas. Misturá-los numa rolagem só fazia o leitor
          encontrar primeiro os números do que não serve. */}
      <h2 className="mt-10 text-lg font-semibold">Detalhe por programa</h2>
      <Tabs defaultValue="PPGPEP" className="mt-4">
        <TabsList>
          <TabsTrigger value="PPGPEP">
            PPGPEP
            <Badge variant="secondary" className="ml-2 font-normal">
              aprovado
            </Badge>
          </TabsTrigger>
          <TabsTrigger value="PPGCC">
            PPGCC
            <Badge variant="outline" className="ml-2 font-normal">
              eliminado
            </Badge>
          </TabsTrigger>
        </TabsList>

        {/* ── PPGPEP ─────────────────────────────────────────────────────── */}
        <TabsContent value="PPGPEP" className="space-y-6">
          <Card>
            <CardContent className="space-y-4 px-6">
              <div>
                <h2 className="font-medium">{ppgpep?.name ?? "PPGPEP"}</h2>
                <p className="text-sm text-muted-foreground">
                  {ppgpep?.institution} {ppgpep?.campus} · mestrado profissional · aulas à noite, de
                  segunda a sexta
                </p>
              </div>
              <Eligibility passes />
              <p className="text-xs text-muted-foreground">
                O edital não oferece bolsa de CAPES ou CNPq (item 11.3). Para quem mantém o vínculo
                com a FAI isso não muda nada — e é o formato que existe justamente para quem
                trabalha.
              </p>
            </CardContent>
          </Card>

          {ppgpepCycle && (
            <>
              <NextSteps cycle={ppgpepCycle} lines={linesOf("PPGPEP")} today={today} />

              <Card>
                <CardContent className="px-6">
                  <Timeline cycle={ppgpepCycle} today={today} />
                </CardContent>
              </Card>

              <CycleCard
                c={ppgpepCycle}
                lines={linesOf("PPGPEP")}
                showSchedule={false}
                showDocuments={false}
              />
            </>
          )}

          <section>
            <h3 className="text-sm font-medium">Linhas de pesquisa</h3>
            <p className="mt-1 mb-3 text-sm text-muted-foreground">
              Passe o mouse na sigla para ver o nome oficial e o que a linha significa. Os docentes
              ainda não foram levantados — é a próxima pesquisa.
            </p>
            <LinesTable program={ppgpep} termCollected={false} />
          </section>
        </TabsContent>

        {/* ── PPGCC ──────────────────────────────────────────────────────── */}
        <TabsContent value="PPGCC" className="space-y-6">
          {eveningOfferings === 0 && (
            <Alert>
              <Ban className="size-4" />
              <AlertDescription>
                <strong>Eliminado: não há oferta noturna.</strong> Nenhuma das {offerings.length}{" "}
                disciplinas deste semestre começa depois das 18:00. Com jornada {WORK}, cursar este
                programa exigiria acordo com o empregador — não é questão de escolher a disciplina
                certa. Os números abaixo descrevem um programa que não é opção; ficam registrados
                porque foram verificados e porque explicam a eliminação.
              </AlertDescription>
            </Alert>
          )}

          <Card>
            <CardContent className="space-y-4 px-6">
              <div>
                <h2 className="font-medium">{ppgcc?.name ?? "PPGCC"}</h2>
                <p className="text-sm text-muted-foreground">
                  {ppgcc?.institution} {ppgcc?.campus}
                  {ppgcc?.capes_rating != null && ` · CAPES ${ppgcc.capes_rating}`}
                </p>
              </div>
              <Eligibility passes={false} failedOn={0} />
            </CardContent>
          </Card>

          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
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

          {cyclesOf("PPGCC").map((c) => (
            <CycleCard key={c.id} c={c} lines={linesOf("PPGCC")} />
          ))}

          <section>
            <h3 className="text-sm font-medium">Grade semanal · 2026/2</h3>
            <p className="mt-1 mb-3 text-sm text-muted-foreground">
              O programa publica apenas duas faixas, e nenhuma é noturna. Passe o mouse numa
              disciplina para ver docente, créditos, salas e idioma.
            </p>
            <ScheduleGrid offerings={offerings} workLabel={WORK} lines={linesOf("PPGCC")} />
          </section>

          <section>
            <h3 className="text-sm font-medium">Linhas de pesquisa</h3>
            <p className="mt-1 mb-3 text-sm text-muted-foreground">
              Passe o mouse na sigla para ver o nome oficial, os docentes e o que a linha significa.
            </p>
            <LinesTable program={ppgcc} termCollected />
          </section>
        </TabsContent>
      </Tabs>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Monitoramento</h2>
        <p className="mt-1 mb-4 text-sm text-muted-foreground">
          O coletor compara o TEXTO extraído, não os bytes — PDF regerado muda byte a byte dizendo a
          mesma coisa, e um monitor que grita à toa ninguém lê. PDF digitalizado, sem texto a
          extrair, cai para os bytes e diz que caiu.
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
