import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The dev server runs inside a container and is reached through Caddy at
  // https://grad-radar.localhost. Next validates the origin of dev-only requests
  // (HMR, server actions) and rejects anything it does not recognise, so the
  // proxied hostname has to be declared here explicitly.
  allowedDevOrigins: ["grad-radar.localhost", "pos.v1cferr.dev"],

  /**
   * `/api/*` também pelo Next, não só pelo Caddy.
   *
   * Em produção o Caddy intercepta /api/* antes de chegar aqui, então isto é
   * inerte lá. Em desenvolvimento, acessando 127.0.0.1:3006 direto, não há Caddy
   * — e o `<iframe>` do visualizador de edital é a PRIMEIRA coisa que o
   * navegador busca em /api. Sem esta reescrita, ele daria 404 só no dev, que é
   * exatamente onde os testes rodam.
   *
   * Mesma origem é o ponto: os PDFs da UFSCar mandam `X-Frame-Options:
   * SAMEORIGIN`, então embutir o endereço original é bloqueado pelo navegador.
   */
  async rewrites() {
    const backend = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
