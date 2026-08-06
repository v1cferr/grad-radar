"use client";

import { useEffect, useState } from "react";

/**
 * Browser-side health probe — the half of the F0 smoke test that exercises the
 * full request path: browser → Caddy → backend → PostgreSQL.
 *
 * It fetches a RELATIVE path (`/api/health`), which is the whole point of
 * putting frontend and API behind a single Caddy host: no CORS, and no backend
 * port baked into the JS bundle.
 */
export function HealthProbe() {
  const [state, setState] = useState("checking…");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL ?? "/api";

    fetch(`${base}/health`, { cache: "no-store" })
      .then(async (res) => setState(`HTTP ${res.status} · ${JSON.stringify(await res.json())}`))
      .catch((err: unknown) => setState(`unreachable · ${String(err)}`));
  }, []);

  return <code className="break-all">{state}</code>;
}
