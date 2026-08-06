import { HealthProbe } from "./health-probe";

/**
 * F0 smoke-test page. Not product UI — it exists to prove the infrastructure
 * before any domain code is written, and it gets replaced in F3.
 *
 * It checks the two request paths that matter, because they fail independently:
 *
 *   1. server-side  — this container → `backend:8000` over the compose network
 *   2. browser-side — browser → Caddy → `backend:8000` (see HealthProbe)
 *
 * A green (1) with a red (2) means Caddy's routing is wrong; a red (1) means the
 * compose network or the backend itself is broken.
 */

async function serverSideHealth(): Promise<string> {
  const base = process.env.BACKEND_INTERNAL_URL;
  if (!base) return "BACKEND_INTERNAL_URL is not set";

  try {
    // no-store: a health check must never be answered from the fetch cache.
    const res = await fetch(`${base}/api/health`, { cache: "no-store" });
    return `HTTP ${res.status} · ${JSON.stringify(await res.json())}`;
  } catch (err: unknown) {
    return `unreachable · ${err instanceof Error ? err.message : String(err)}`;
  }
}

export default async function Home() {
  const serverStatus = await serverSideHealth();

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-8 p-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">GradRadar</h1>
        <p className="mt-1 text-neutral-600 dark:text-neutral-400">
          Discover, compare, and track graduate opportunities.
        </p>
      </header>

      <section className="rounded-lg border border-neutral-200 p-5 text-sm dark:border-neutral-800">
        <h2 className="font-medium">Infrastructure smoke test</h2>
        <dl className="mt-4 space-y-3">
          <div>
            <dt className="text-neutral-600 dark:text-neutral-400">
              Server-side (container → backend)
            </dt>
            <dd className="mt-0.5 font-mono text-xs">{serverStatus}</dd>
          </div>
          <div>
            <dt className="text-neutral-600 dark:text-neutral-400">
              Browser-side (browser → Caddy → backend)
            </dt>
            <dd className="mt-0.5 font-mono text-xs">
              <HealthProbe />
            </dd>
          </div>
        </dl>
      </section>

      <p className="text-xs text-neutral-500">
        F0 — infrastructure only. The data model, API and real UI land in F1–F3.
      </p>
    </main>
  );
}
