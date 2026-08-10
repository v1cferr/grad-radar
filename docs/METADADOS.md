# Metadados

O link é o produto. Ele vai por WhatsApp para o JP e o César, e é assim que eles
descobrem que existe prazo. Um preview quebrado não gera erro em lugar nenhum — a
mensagem simplesmente chega como URL crua, e ninguém abre. Por isso os metadados
são testados como código de produção, em
[`frontend/web/e2e/metadata.spec.ts`](../frontend/web/e2e/metadata.spec.ts).

## A decisão central: pública, mas fora de índice

A página é aberta, sem autenticação, porque o login vai morar na aplicação e uma
senha de proxy na frente significaria digitar duas
([`dotfiles/system/services/caddy.nix`](https://github.com/v1cferr/dotfiles)).
Aberta não é o mesmo que indexável: é a busca de pós-graduação de três pessoas
específicas, e um resultado de pesquisa sobreviveria ao projeto.

Então: **`noindex, nofollow` + `robots.txt` com `Disallow: /`**.

Isso **não custa o preview do WhatsApp.** WhatsApp, Telegram e Slack buscam a URL
diretamente e leem as tags OG do HTML que receberam. `noindex` é diretiva para
índice de **busca** — quem monta preview não consulta índice nenhum, e não pede
robots.txt para uma URL que o usuário acabou de colar. As duas coisas coexistem, e
é exatamente o que se quer: rico no canal que usamos, invisível no que não usamos.

Os dois mecanismos são necessários e fazem coisas diferentes:

| | Instrui quem | Sem ele |
| --- | --- | --- |
| `<meta name="robots">` | já baixou a página | a URL pode aparecer em resultado por links externos |
| `/robots.txt` | está decidindo se baixa | não impede indexação de quem chegou por link |

## Nada que possa envelhecer errado

Título, descrição e imagem carregam o edital vigente — mas **nenhum deles mostra
contagem de dias**, e isso é deliberado.

Clientes de chat cacheiam o preview inteiro por URL, agressivamente e por tempo
indeterminado. Um "faltam 36 dias" renderizado hoje continuaria sendo entregue em
outubro, afirmando um número errado com toda a confiança. A data absoluta — "até
14 de setembro de 2026" — é verdadeira em qualquer momento que for lida.

É a mesma regra que vale no resto do projeto: preferir o campo que não pode ficar
errado em silêncio. Um prazo errado é pior que prazo nenhum, porque parece
informação. Há um teste que falha se um número de dias voltar para o título ou a
descrição.

A contagem continua na página, onde é renderizada a cada acesso e não pode
envelhecer.

## Por que a imagem é uma rota, não `opengraph-image.tsx`

A convenção de arquivo do Next é o caminho recomendado, e não serve aqui.

Ela emitia `og:image` apontando para **`http://localhost:3000/opengraph-image`**
mesmo com `metadataBase` corretamente configurado — o `og:url` ao lado saía como
`https://pos.v1cferr.dev`, então o `metadataBase` estava certo. A URL da imagem é
resolvida contra a origem do servidor de desenvolvimento, e este deploy roda
`next dev` de propósito
([`dotfiles/system/services/grad-radar.nix`](https://github.com/v1cferr/dotfiles)).
O crawler receberia um endereço que não existe para ele, e o link sairia sem
imagem.

Não dava para corrigir por cima: **metadados por arquivo têm prioridade sobre o
objeto `metadata`**, então declarar a URL absoluta era ignorado. Foi preciso tirar
a convenção do caminho — a imagem virou [`app/og/route.tsx`](../frontend/web/src/app/og/route.tsx),
e quem monta a tag é o layout, a partir de `SITE_URL`.

Descartado antes disso: limpar o volume `.next`, para excluir cache. O hash da URL
saiu idêntico com o volume recriado, o que provou ser comportamento e não cache.

## A pegadinha do merge raso

O merge de metadata do Next é **raso**. Um `openGraph` declarado na página
substitui o do layout **inteiro** em vez de completá-lo.

Isso já aconteceu aqui: definir `openGraph: { title, description }` na página
apagou `type`, `locale`, `siteName`, `url` e a imagem. Sem erro, sem aviso — as
tags simplesmente deixaram de existir no HTML. Foi encontrado inspecionando o
`<head>` renderizado, não pelo `tsc`.

A defesa são `OG_BASE` e `TWITTER_BASE` em
[`lib/site.ts`](../frontend/web/src/lib/site.ts), feitas para spread, mais um
teste que verifica as quatro tags do layout na página que as sobrescreve.

## Ícones

| Arquivo | Para que | Por que assim |
| --- | --- | --- |
| `app/icon.svg` | aba do navegador | SVG escala de 16px a 512px sem um arquivo por tamanho; fundo azul sólido porque um traço fino desaparece em barra clara **ou** escura |
| `app/apple-icon.tsx` | tela inicial do iOS | `apple-touch-icon` **não aceita SVG** — só jpg/png. Sem ele o iOS usa um print reduzido da página |
| `app/manifest.ts` | "adicionar à tela inicial" | o uso real é no celular; sem manifesto o atalho nasce com o nome do domínio |

Sem cantos arredondados no `apple-icon`: o iOS aplica a máscara dele, e arredondar
aqui produziria borda dupla.

## O contrato de ambiente

`SITE_URL` entrou no [`.env.example`](../.env.example). Alimenta o `metadataBase`,
de onde saem o canonical e a URL absoluta da imagem. O default no código é o
domínio real, não um placeholder — a variável existe para que um ambiente
diferente não precise de mudança de código.

**`docker compose restart` não relê o `env_file`.** Uma variável nova exige
`up -d` para recriar o container. Isto custou uma medição errada: com `SITE_URL`
vazio o `metadataBase` caía no default e o canonical saía certo, o que dava a
impressão de estar tudo configurado.

## Deixado de fora

- **`sitemap.ts`** — um sitemap serve para orientar indexação, e a página está
  fora de índice por decisão. Emitir os dois seria contraditório.
- **`verification`** (Google Search Console e afins) — não há nada a verificar em
  quem não quer ser indexado.
- **`keywords`** — ignorado por buscadores há anos, e não haveria buscador aqui.
