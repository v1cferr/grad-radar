# Automação: o que tirar da mão

O objetivo é claro: ninguém — nem o Victor, nem um assistente por trás de um CLI —
deve precisar abrir PDF para saber se um programa tem aula à noite. Este documento
diz qual parte disso vale automatizar, qual não, e por quê.

## O que a varredura manual realmente fez

Vale separar, porque as duas metades têm custos muito diferentes:

| Metade | O que é | Custo real |
| --- | --- | --- |
| **Buscar** | achar a URL, seguir o redirect do SEI, extrair texto do PDF | baixo — o coletor já faz, 19 fontes, 2×/dia |
| **Interpretar** | ler `8h às 12h` e concluir "sem oferta noturna" | foi o gargalo, e é o que dá para automatizar |

Buscar já está resolvido. O que consumiu atenção foi ler dez documentos e decidir o
que cada um significava.

## Playwright: não, e vale explicar

A ideia inicial era Playwright para tudo. Recomendo **não**, com evidência: das dez
páginas lidas na varredura de 10/08 — ProPG, ICMC, PPGCTS, PPGEP, PPGCI, PPGAdS,
MECAI e três PDFs no SEI — **nenhuma** exigiu JavaScript. Todas eram HTML
renderizado no servidor ou PDF, e `httpx` + BeautifulSoup + `pypdf` pegou tudo,
incluindo seguir o 302 para dentro do SEI.

Playwright custaria um navegador por fetch (centenas de MB de RAM, segundos por
página) para comprar zero nessas fontes. Pior: adiciona uma superfície de falha
grande — versão de browser, timeout, seletor — num componente cujo trabalho é
justamente **nunca** falhar em silêncio.

O desenho certo é uma flag por fonte: `httpx` como padrão, Playwright como
**fallback opcional** para o dia em que aparecer um site que só renderize com JS.
Pagar o custo onde ele compra algo, e não antes.

## Ollama: onde o modelo ajuda, e onde estraga

O host já tem Ollama ligado (`dotfiles/system/services/ollama.nix`), com `qwen3:4b`
e `bge-m3`, GPU Intel Arc B580 por Vulkan.

### Onde NÃO usar o modelo

**Detectar horário.** Regex resolveu os seis documentos de grade, todos: `8h às 12h`,
`14h às 17h`, `08h–12h`, `14h–18h`, `08:00–09:40`. Só o PPGCI usa prosa em vez de
número — "Horário de oferta: Manhã e Tarde" —, e isso é uma tabela de vocabulário
de cinco palavras, não um modelo de linguagem.

Regex é determinística, testável e **não inventa**. Um modelo que alucina "há
disciplina às 19h" produz exatamente a falha que este projeto existe para evitar, e
com aparência de resposta.

### Onde usar

**Extrair campos de edital.** É prosa longa, em formatos que variam por programa:
janela de inscrição, vagas, etapas, documentos exigidos, data do resultado. Foi aqui
que a leitura humana pesou de verdade — e é aqui que um modelo pequeno rende, porque
a tarefa é achar campos conhecidos em texto desconhecido.

Sugestão de modelo: **`qwen3:8b`** em vez do `4b` atual. Contexto de 32K (o edital
do MECAI extraiu 33.733 caracteres, ~10K tokens — cabe), modo JSON, bom em
português, e Q4 em 8B ocupa ~5 GB dos 12 GB da Arc B580. O `bge-m3` continua
servindo se algum dia houver busca semântica sobre snapshots.

### A regra que não se negocia

> **Um modelo nunca é a fonte de uma data.**

Toda extração por LLM entra como **proposta**, ligada ao `source_snapshot` de onde
saiu, e é exibida ao lado do trecho citado. O número que aparece no card de prazo só
vem de campo confirmado.

O motivo é o custo assimétrico: uma extração errada que ninguém revisa faz vocês
perderem um prazo, que é o dano máximo possível aqui. Um campo vazio faz alguém
abrir o PDF, que é chato e recuperável.

Isso não é desconfiança de modelo pequeno — valeria igual para um modelo grande. O
sistema já trata "desconhecido" como diferente de "não" em todo lugar; uma proposta
não confirmada é a mesma ideia.

## A ordem que eu faria

1. **Extrator de faixas horárias, determinístico.** Recebe o texto de um documento e
   devolve as faixas + veredito do requisito 1. Já existem **seis fixtures reais com
   resposta conhecida** — PPGCC, PPGEE, PIPGEs, PPGCTS, PPGEP e PPGCI —, então o
   teste de regressão nasce junto. É o passo que tira a leitura manual do circuito.
2. **Notificação (F4).** O `.env.example` já reserva as variáveis. Sem isso, o
   monitor detecta a mudança e ninguém fica sabendo — o que é quase o problema
   original de volta.
3. **Extração de edital por LLM, como proposta.** Só depois de 1 e 2: é a peça mais
   complexa e a única que pode errar de forma perigosa.
4. **Playwright como fallback por fonte.** Quando alguma fonte pedir.

O item 2 vale mais que o 3. Um monitor que detecta e não avisa é um monitor que
ninguém lê.

## Uma armadilha achada na varredura: o soft 404

O ICMC responde **HTTP 200 com uma página de erro** para URLs que não existem
(`/pos-graduacao/ccmc` e `/pos-graduacao/ccmc/disciplinas` fazem isso). O coletor
registra sucesso, extrai o texto da página de erro e segue.

Consequência real: se uma fonte vigiada começar a soft-404 — reorganização de
site, URL renomeada —, o monitor vai reportar "mudou" uma vez e "igual" para
sempre. **Nunca "falhou".** É a falha silenciosa clássica, e o painel de
monitoramento mostraria tudo verde.

Correção sugerida, junto com o extrator: uma heurística de sanidade por fonte —
tamanho mínimo de texto esperado, ou ausência de marcadores como "Erro 404" /
"Page not found" no conteúdo extraído. Não precisa de modelo; precisa de uma
asserção.

## O que continua humano

- **Julgar aderência.** Os cinco sinais de [`ADERENCIA.md`](ADERENCIA.md) são leitura
  de escopo, não extração de campo. Um modelo pode sugerir; o veredito é editorial e
  fica marcado como tal (`verified = false`).
- **PDF digitalizado.** O edital do PPGPEP são 18 páginas de imagem sem camada de
  texto. Isso pede OCR, não LLM — e o coletor já detecta o caso e cai para hash de
  bytes, então ao menos a **mudança** é percebida.
