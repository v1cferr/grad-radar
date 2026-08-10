import type { MetadataRoute } from "next";

/**
 * Manifesto para "adicionar à tela inicial".
 *
 * O uso real deste projeto é no celular — o link vai por WhatsApp e é no
 * telefone que os três abrem. Sem manifesto, o atalho na tela inicial nasce com
 * o nome do domínio e abre numa aba comum do navegador.
 *
 * `display: "standalone"` porque não há navegação: é uma página só, e a barra de
 * endereço só ocupa altura numa tela onde a grade horária já disputa espaço.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "GradRadar — pós-graduação com aula à noite",
    short_name: "GradRadar",
    description:
      "Processos seletivos de pós-graduação pública, gratuita, presencial em São Carlos e noturna.",
    lang: "pt-BR",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#2a78d6",
    icons: [
      { src: "/icon.svg", type: "image/svg+xml", sizes: "any", purpose: "any" },
      { src: "/apple-icon", type: "image/png", sizes: "180x180" },
    ],
  };
}
