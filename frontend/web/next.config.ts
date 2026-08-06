import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The dev server runs inside a container and is reached through Caddy at
  // https://grad-radar.localhost. Next validates the origin of dev-only requests
  // (HMR, server actions) and rejects anything it does not recognise, so the
  // proxied hostname has to be declared here explicitly.
  allowedDevOrigins: ["grad-radar.localhost"],
};

export default nextConfig;
