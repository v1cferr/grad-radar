import { defineConfig, devices } from "@playwright/test";

/**
 * E2E against the RUNNING stack — the real Caddy, the real Next server, the real
 * database. Nothing is mocked, because the point of this layer is exactly what
 * the in-process API tests cannot reach: that a browser renders the data.
 *
 * `pos.v1cferr.dev` resolves here through the router's split-DNS and serves a
 * real Let's Encrypt certificate, so no `ignoreHTTPSErrors` is needed. From the
 * LAN Caddy skips basic auth, which is why these tests carry no credentials.
 *
 * Browsers come from the Nix devShell (PLAYWRIGHT_BROWSERS_PATH); the
 * @playwright/test version in package.json must match the driver version the
 * shellHook prints.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  // A test that only passes sometimes is a test that tells you nothing.
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "https://pos.v1cferr.dev",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
