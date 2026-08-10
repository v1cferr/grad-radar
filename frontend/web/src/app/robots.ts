import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

/**
 * Fora de todo índice de busca.
 *
 * O `robots` do metadata já emite a meta tag; este arquivo emite o
 * /robots.txt. Os dois são necessários e fazem coisas diferentes: a meta tag
 * instrui quem já BAIXOU a página, o robots.txt instrui quem está decidindo se
 * vai baixar. Só a meta tag deixaria a URL aparecer em resultado por links
 * externos; só o robots.txt não impediria indexação de quem chegou por link.
 *
 * Não afeta preview de link: o crawler do WhatsApp não consulta robots.txt para
 * montar preview de uma URL que o usuário colou. Ver o comentário em layout.tsx.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", disallow: "/" },
    host: SITE_URL,
  };
}
