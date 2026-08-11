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

1. ~~**Extrator de faixas horárias, determinístico.**~~ **Feito** — ver abaixo.
2. ~~**Notificação (F4).**~~ **Feito** — ver abaixo.
3. **Extração de edital por LLM, como proposta.** Só depois de 1 e 2: é a peça mais
   complexa e a única que pode errar de forma perigosa.
4. **Playwright como fallback por fonte.** Quando alguma fonte pedir.

O item 2 valia mais que o 3, e foi feito primeiro por isso.

## A notificação, e o que ela se recusa a mandar

`app/notify.py`, rodando no fim da cadeia do timer: coleta → reavalia horário →
avisa. Por último de propósito, porque lê o que os dois anteriores acabaram de
gravar.

**Não existe evento "conteúdo mudou".** Essa é a decisão central. O hash de uma
página muda por motivo nenhum — contador de visitas, PDF regerado, banner rotativo
— e um canal que avisa disso ensina a ignorar o canal. Depois do terceiro alerta
inútil, o quarto não é lido, e o que estava no quarto era o edital.

São cinco eventos, e cada um responde a "isso faz alguém agir?":

| Evento | Faz agir porque |
| --- | --- |
| `announcement` | apareceu **anúncio de processo** numa página vigiada |
| `cycle_open` | apareceu processo que dá para fazer |
| `deadline_soon` | o prazo está chegando e o projeto leva semanas |
| `notice_changed` | o **edital** mudou — retificação muda regra |
| `source_blind` | paramos de conseguir ver uma fonte; o silêncio virou cegueira |
| `schedule_verdict` | a grade mudou o veredito de horário |

O `schedule_verdict` é o mais valioso a longo prazo: é ele que avisa se o PPGCC
abrir aula à noite. O `announcement` é o que responde "como vamos saber quando
sair um edital novo".

### O buraco que o `announcement` fechou

A primeira versão do notificador avisava sobre edital alterado apenas para fontes
do tipo `EDITAL_PDF`. Mas o Edital 01/2026 do PPGAdS **apareceu numa
`admission_page`** — a página de processos seletivos ganhou três linhas novas. Ou
seja: se aquele edital tivesse aparecido com o notificador rodando, **ninguém teria
sido avisado.** Foi encontrado à mão, porque o Victor perguntou como o
acompanhamento funcionaria dali para frente.

Agora `ADMISSION_PAGE` e `PROGRAM_INDEX` também disparam, mas **não por mudança de
hash**: o evento compara os dois últimos snapshots, pega as linhas
**acrescentadas** e só avisa se alguma parecer anúncio — "edital", "processo
seletivo", "inscrições", "vagas", "ingresso".

Duas consequências que valem mais que a detecção em si:

- **O aviso diz O QUE apareceu.** O corpo da mensagem cita as linhas novas, então
  a notificação lê "Processo Seletivo 2026 / Para a turma que iniciará as atividades
  em 2027" em vez de "a página mudou". A diferença entre um alerta que se lê e um
  que se arquiva.
- **Texto de navegação não conta.** Só adições entram no diff, e o menu já estava
  lá antes. A chave de dedupe é o hash das linhas ACRESCENTADAS, não da página — a
  página muda de novo por outros motivos e o mesmo anúncio não volta.

O caso real está no teste, verbatim, em `tests/test_notify.py`.

### Três detalhes que decidem se o canal é lido

**Lembretes são marcos, não diários.** 30, 14, 7, 3 e 1 dia. Um alerta por dia
durante cinco semanas treina a pessoa a arquivar sem ler, e o dia que importa fica
indistinguível dos vinte anteriores. E é o marco **mais apertado já cruzado** que
dispara — um bug real pego por teste: iterar a tupla decrescente e parar no
primeiro `left <= marco` casava sempre o 30, então com sete dias restantes o aviso
diria "faltam 30 dias".

**A deduplicação é do banco, não da lógica.** `dedupe_key` é UNIQUE. Um `if` pode
ficar de fora de um caminho novo; uma constraint não. E o marco sobrevive à máquina
desligada: com `Persistent = true` no timer, uma checagem perdida roda atrasada e o
marco não é nem perdido nem repetido.

**Entregue só quando algum canal aceitou.** `delivered_at` fica nulo se todos
falharem, e a nota registra o erro por canal. Gravar entregue sem entrega tornaria
a tabela um registro de mentiras — e o dedupe garantiria que nunca mais se
tentasse.

### Canais

**ntfy primeiro**, porque já é o padrão do host: os dotfiles usam ntfy para o
duo-streak-daemon, então o app está no celular e o hábito existe. Zero papelada —
o tópico é a credencial.

**Telegram** como segundo, também sem custo.

**E-mail** como terceiro, e é o que eu recomendo ligar junto com o ntfy: chega onde
os três já olham durante o trabalho, sem instalar nada.

**WhatsApp continua não implementado**, e a decisão está em
[`WHATSAPP.md`](WHATSAPP.md) porque é de risco, não de arquitetura. Resumo: dá para
usar o número próprio com bibliotecas FOSS (Baileys, whatsmeow, Evolution API), mas
em 2025–2026 o WhatsApp baniu contas de uso legítimo e baixo volume usando essas
bibliotecas — e a detecção pondera muito a **razão de resposta**, que num bot de
notificação é zero. Este caso de uso é o perfil que o classificador procura, não uma
exceção improvável. Com o número da FAI, o custo de um banimento é perder o número
de trabalho.

Um canal só conta como ativo se as credenciais dele existirem. Canal declarado sem
credencial falharia calado a cada execução, e o sintoma — "não recebo nada" — é
idêntico a "não houve novidade".

## O extrator, já em pé

`app/extract.py` recebe o texto de um documento e devolve as faixas horárias mais
o veredito do requisito 1, com a frase que o sustenta. Nenhum modelo envolvido.

Testado contra **oito documentos reais**, cada um com a resposta que uma pessoa
produziu lendo o mesmo texto: PPGCC, PPGEE, PIPGEs, PPGCTS, PPGEP, PPGCI, o edital
do MECAI e a página de erro do ICMC. Se o extrator discordar da leitura humana em
qualquer um, o teste falha.

Três regras que ele codifica, e que foram as decisões difíceis da varredura manual:

- **A regra é sobre o INÍCIO da aula, não o fim.** Uma disciplina de 14h às 18h
  conflita integralmente com quem trabalha até as 18h. Foi assim que o PPGEP e o
  PPGEE caíram — a última faixa deles termina quando a jornada termina, e olhar o
  fim os teria aprovado por engano.
- **Permissão não é oferta.** "As aulas poderão ser oferecidas no período noturno"
  devolve `unknown`, não `met`. Foi exatamente essa distinção que separou o veredito
  certo do errado no MECAI, e ela está numa lista de hedges — "poderão",
  "podendo", "preferencialmente".
- **Faixa numérica ganha de prosa.** A palavra "noturno" num rodapé não sobrepõe
  uma grade que mostra 8h–12h e 14h–17h.

### O laço fechado: `just verify`

`app/verify.py` relê as grades que o monitor já baixou, roda o extrator e compara
com o veredito gravado no banco. Roda junto do monitor, duas vezes por dia, pelo
mesmo timer.

Quando a grade de 2027/1 sair, isto responde "o PPGCC passou a ter faixa às 19h"
sem ninguém abrir PDF. É a pergunta que custou seis leituras manuais.

**Relata, não grava.** Divergência pode ser grade nova — o que se quer saber — ou o
extrator falhando num formato inédito. Gravar em silêncio apagaria a diferença, e o
segundo caso é o que corrompe a decisão. `just verify-apply` grava, depois de
alguém ler a evidência.

Uma coisa que só apareceu quando o verificador rodou: `unknown` do extrator **não é
discordância**. Um catálogo que lista disciplinas sem horário não contradiz um
veredito verificado — só não tem o que dizer. Tratar como divergência enchia o
relatório de ruído e escondia a única linha que importava. É a regra do projeto
("desconhecido ≠ não") aplicada à própria ferramenta.

Para isso funcionar, `Source` ganhou `program_id`: era o elo que faltava entre um
documento e uma decisão. 17 das 19 fontes estão ligadas a um programa; as duas
restantes são catálogos institucionais, que falam de todos.

## Uma armadilha achada na varredura: o soft 404

O ICMC responde **HTTP 200 com uma página de erro** para URLs que não existem
(`/pos-graduacao/ccmc` e `/pos-graduacao/ccmc/disciplinas` fazem isso). O coletor
registra sucesso, extrai o texto da página de erro e segue.

Consequência real: se uma fonte vigiada começar a soft-404 — reorganização de
site, URL renomeada —, o monitor vai reportar "mudou" uma vez e "igual" para
sempre. **Nunca "falhou".** É a falha silenciosa clássica, e o painel de
monitoramento mostraria tudo verde.

**Corrigido.** `is_error_page()` casa marcadores explícitos — "Erro 404", "página
não encontrada" — e apenas nos primeiros 400 caracteres, para que um edital que
mencione "não encontrado" na página 12 não seja confundido com uma página de erro.
O monitor agora marca essas coletas como suspeitas e as conta separadamente; o
`verify` se recusa a derivar veredito delas.

## O que continua humano

- **Julgar aderência.** Os cinco sinais de [`ADERENCIA.md`](ADERENCIA.md) são leitura
  de escopo, não extração de campo. Um modelo pode sugerir; o veredito é editorial e
  fica marcado como tal (`verified = false`).
- **PDF digitalizado.** O edital do PPGPEP são 18 páginas de imagem sem camada de
  texto. Isso pede OCR, não LLM — e o coletor já detecta o caso e cai para hash de
  bytes, então ao menos a **mudança** é percebida.
