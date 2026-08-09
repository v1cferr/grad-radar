"use client";

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import {
  ArrowUpDown,
  Check,
  CircleHelp,
  ExternalLink,
  Search,
  X,
} from "lucide-react";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { Option, RequirementStatus } from "@/lib/api";
import { fmt } from "@/lib/format";

const REQ_LABEL: Record<string, { short: string; full: string }> = {
  evening_classes: { short: "Noite", full: "Aula à noite — os três trabalham 08–18" },
  in_person_sao_carlos: {
    short: "S. Carlos",
    full: "Presencial em São Carlos — mudar de cidade não está em questão",
  },
  tuition_free: { short: "Grátis", full: "Sem mensalidade" },
  public_institution: { short: "Pública", full: "Universidade pública" },
};

const VERDICT: Record<string, { text: string; color: string }> = {
  approved: { text: "aprovado", color: "var(--status-good)" },
  pending: { text: "falta verificar", color: "var(--status-warning)" },
  eliminated: { text: "eliminado", color: "var(--status-critical)" },
};

/** Estado + ícone + rótulo. Nunca só a cor: quem não distingue verde de vermelho
 *  precisa ler a mesma coisa que os outros. */
function ReqCell({
  status,
  evidence,
  label,
}: {
  status: RequirementStatus;
  evidence: string | null;
  label: string;
}) {
  const Icon = status === "met" ? Check : status === "not_met" ? X : CircleHelp;
  const color =
    status === "met"
      ? "var(--status-good)"
      : status === "not_met"
        ? "var(--status-critical)"
        : "var(--muted-foreground)";
  const word = status === "met" ? "atende" : status === "not_met" ? "não atende" : "não verificado";

  return (
    <Tooltip>
      <TooltipTrigger
        render={<span tabIndex={0} className="inline-flex cursor-help items-center gap-1" />}
      >
        <>
          <Icon className="size-4" style={{ color }} aria-hidden />
          <span className="sr-only">
            {label}: {word}
          </span>
        </>
      </TooltipTrigger>
      <TooltipContent className="max-w-sm">
        <div className="space-y-1">
          <div className="font-medium">
            {label} — {word}
          </div>
          {/* A evidência é o ponto: "eliminado" sem o porquê obriga a refazer a
              pesquisa toda vez que alguém duvidar. */}
          {evidence ? (
            <p className="text-[11px] leading-relaxed opacity-90">{evidence}</p>
          ) : (
            <p className="text-[11px] opacity-70">Ainda não pesquisado.</p>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}

function sortable(label: string) {
  return function Header({ column }: { column: { toggleSorting: (d?: boolean) => void } }) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="-ml-3 h-8"
        onClick={() => column.toggleSorting()}
      >
        {label}
        <ArrowUpDown className="ml-1.5 size-3.5 opacity-50" aria-hidden />
      </Button>
    );
  };
}

const columns: ColumnDef<Option>[] = [
  {
    accessorKey: "acronym",
    header: sortable("Programa"),
    cell: ({ row }) => {
      const o = row.original;
      return (
        <div className="min-w-40">
          <div className="flex items-center gap-1.5 font-medium">
            {o.acronym}
            {o.website && (
              <a
                href={o.website}
                className="text-muted-foreground hover:text-foreground"
                aria-label={`Site do ${o.acronym}`}
              >
                <ExternalLink className="size-3" />
              </a>
            )}
          </div>
          <div className="text-xs text-muted-foreground">{o.name}</div>
        </div>
      );
    },
  },
  {
    accessorKey: "institution",
    header: sortable("Instituição"),
    cell: ({ row }) => (
      <span className="text-sm whitespace-nowrap">
        {row.original.institution}
        <span className="text-muted-foreground"> · {row.original.campus}</span>
      </span>
    ),
  },
  ...(["evening_classes", "in_person_sao_carlos", "tuition_free", "public_institution"] as const).map(
    (key): ColumnDef<Option> => ({
      id: key,
      header: () => (
        <span className="text-xs whitespace-nowrap">{REQ_LABEL[key].short}</span>
      ),
      cell: ({ row }) => {
        const r = row.original.requirements.find((x) => x.requirement === key);
        return (
          <ReqCell
            status={r?.status ?? "unknown"}
            evidence={r?.evidence ?? null}
            label={REQ_LABEL[key].full}
          />
        );
      },
    }),
  ),
  {
    accessorKey: "verdict",
    header: sortable("Veredito"),
    cell: ({ row }) => {
      const v = VERDICT[row.original.verdict] ?? VERDICT.pending;
      return (
        <Badge
          variant="outline"
          className="gap-1.5 whitespace-nowrap"
          style={{ borderColor: v.color }}
        >
          <span aria-hidden className="size-2 rounded-full" style={{ background: v.color }} />
          {v.text}
        </Badge>
      );
    },
  },
  {
    id: "prazo",
    accessorFn: (o) => o.days_left ?? Number.MAX_SAFE_INTEGER,
    header: sortable("Prazo"),
    cell: ({ row }) => {
      const o = row.original;
      if (o.days_left === null) {
        return (
          <span className="text-xs text-muted-foreground">
            {o.applications_close_on ? "encerrado" : "sem processo aberto"}
          </span>
        );
      }
      return (
        <div className="whitespace-nowrap">
          <div className="text-sm font-medium tabular-nums">{o.days_left} dias</div>
          <div className="text-xs text-muted-foreground">
            até {fmt(o.applications_close_on)} · {o.total_seats} vagas
          </div>
        </div>
      );
    },
  },
];

/**
 * Todas as opções investigadas, aprovadas e eliminadas.
 *
 * Os eliminados ficam na tabela de propósito. "Já olhamos esse?" é uma pergunta
 * tão cara quanto "qual serve?", e uma lista só de aprovados faz a mesma
 * varredura ser refeita todo mês. Eles vêm por último e com a evidência da
 * eliminação a um hover de distância.
 */
export function OptionsTable({ options }: { options: Option[] }) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [filter, setFilter] = React.useState("");
  const [onlyViable, setOnlyViable] = React.useState(false);

  const data = React.useMemo(
    () => (onlyViable ? options.filter((o) => o.verdict !== "eliminated") : options),
    [options, onlyViable],
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const eliminated = options.filter((o) => o.verdict === "eliminated").length;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 sm:max-w-64">
          <Search
            className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrar por programa ou instituição"
            className="pl-8"
            aria-label="Filtrar opções"
          />
        </div>
        <Button
          variant={onlyViable ? "default" : "outline"}
          size="sm"
          onClick={() => setOnlyViable((v) => !v)}
        >
          {onlyViable ? "Mostrando só viáveis" : `Ocultar ${eliminated} eliminados`}
        </Button>
      </div>

      <Card className="overflow-x-auto py-0">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((h) => (
                  <TableHead key={h.id}>
                    {h.isPlaceholder
                      ? null
                      : flexRender(h.column.columnDef.header, h.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-20 text-center text-sm text-muted-foreground">
                  Nenhum programa corresponde ao filtro.
                </TableCell>
              </TableRow>
            )}
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-verdict={row.original.verdict}
                className={row.original.verdict === "eliminated" ? "opacity-60" : undefined}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <p className="text-xs text-muted-foreground">
        Passe o mouse em qualquer ✓, ✗ ou ? para ver a evidência e a data em que o fato foi
        verificado. Um <strong>?</strong> não é um "não" — é trabalho pendente.
      </p>
    </div>
  );
}
