/**
 * Typed access to the GradRadar API.
 *
 * Server components call this, so it uses BACKEND_INTERNAL_URL (container →
 * container). The browser never talks to the backend directly; it only receives
 * rendered HTML, which is why no CORS configuration exists anywhere.
 */

const BASE = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";

export type Weekday = "monday" | "tuesday" | "wednesday" | "thursday" | "friday";

export type ResearchLine = {
  id: number;
  acronym: string;
  name: string;
  faculty_count: number;
  /** Plain-language gloss — ours, not the institution's. */
  description: string | null;
  /** Disciplines this line actually taught in the current term. */
  offerings: string[];
};

export type RequirementStatus = "met" | "not_met" | "unknown";

/** Uma linha da tabela de opções: um programa e por que ele entra ou sai. */
export type Option = {
  program_id: number;
  acronym: string;
  name: string;
  institution: string;
  campus: string;
  website: string | null;
  capes_rating: number | null;
  verdict: "approved" | "pending" | "eliminated";
  requirements: {
    requirement: string;
    status: RequirementStatus;
    /** O texto que sustenta o veredito. Sem ele, "eliminado" é só uma opinião. */
    evidence: string | null;
  }[];
  research_lines: string[];
  applications_open_on: string | null;
  applications_close_on: string | null;
  cycle_status: string | null;
  total_seats: number | null;
  days_left: number | null;
};

export type Program = {
  id: number;
  name: string;
  acronym: string;
  website: string | null;
  capes_rating: number | null;
  tuition_free: boolean | null;
  institution: string;
  campus: string;
  research_lines: ResearchLine[];
};

export type Stage = {
  ordinal: number;
  name: string;
  starts_on: string | null;
  ends_on: string | null;
  result_on: string | null;
};

export type Cycle = {
  id: number;
  program: string;
  year: number;
  semester: number;
  entry_mode: string;
  degree_level: string | null;
  applications_open_on: string | null;
  applications_close_on: string | null;
  /** Quando o candidato finalmente sabe — depois do último prazo de recurso. */
  final_result_on: string | null;
  site_label: string | null;
  official_url: string | null;
  status: string;
  total_seats: number;
  seats: { research_line: string | null; seats: number }[];
  stages: Stage[];
  required_documents: string[];
};

export type Offering = {
  id: number;
  code: string;
  name: string;
  name_en: string | null;
  credits: number | null;
  year: number;
  semester: number;
  weekday: Weekday | null;
  starts_at: string | null;
  ends_at: string | null;
  language: string | null;
  scope: string | null;
  research_line: string | null;
  professor: string | null;
  locations: string[];
  /** null = schedule unknown. Deliberately distinct from false. */
  conflicts_with_work: boolean | null;
};

export type Source = {
  id: number;
  url: string;
  title: string | null;
  source_type: string;
  active: boolean;
  last_checked_at: string | null;
  redirects_to: string | null;
  last_status: number | null;
  last_error: string | null;
  /** null = never changed since we started watching — not "never checked". */
  last_change_at: string | null;
  checks: number;
};

async function get<T>(path: string): Promise<T> {
  // no-store: this is a tracking dashboard; a cached deadline is a wrong deadline.
  const res = await fetch(`${BASE}/api${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export const getPrograms = () => get<Program[]>("/programs");
export const getCycles = () => get<Cycle[]>("/admission-cycles");
export const getOfferings = (candidate: string) =>
  get<Offering[]>(`/offerings?candidate=${encodeURIComponent(candidate)}`);
export const getSources = () => get<Source[]>("/sources");
export const getOptions = () => get<Option[]>("/options");
