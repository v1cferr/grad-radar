# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: dashboard.spec.ts >> shows the admission timeline with dated stages
- Location: e2e/dashboard.spec.ts:98:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/Análise documental/)
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText(/Análise documental/)

```

```yaml
- main:
  - heading "GradRadar" [level=1]
  - paragraph: Pós-graduação pública, gratuita, presencial em São Carlos e com aula à noite · 10 programas acompanhados
  - paragraph: PPGPEP — inscrições abrem 20 de agosto de 2026 a 14 de setembro de 2026
  - paragraph:
    - text: É o único processo aberto que atende aos quatro requisitos. A seleção é inteiramente sobre um
    - strong: projeto de pesquisa
    - text: — não há prova de conteúdo —, e ele precisa estar escrito antes de a inscrição abrir.
  - text: 36 dias até fechar
  - heading "Opções" [level=2]
  - paragraph: Todos os programas já investigados, com os quatro requisitos eliminatórios lado a lado. Os eliminados continuam aqui — saber que um programa já foi olhado evita refazer a varredura, e a evidência da eliminação fica a um hover de distância.
  - textbox "Filtrar opções":
    - /placeholder: Filtrar por programa ou instituição
  - button "Ocultar 6 eliminados"
  - table:
    - rowgroup:
      - row "Programa Instituição Noite S. Carlos Grátis Pública Veredito Aderência Edital Prazo":
        - columnheader "Programa":
          - button "Programa"
        - columnheader "Instituição":
          - button "Instituição"
        - columnheader "Noite"
        - columnheader "S. Carlos"
        - columnheader "Grátis"
        - columnheader "Pública"
        - columnheader "Veredito":
          - button "Veredito"
        - columnheader "Aderência":
          - button "Aderência"
        - columnheader "Edital"
        - columnheader "Prazo":
          - button "Prazo"
    - rowgroup:
      - 'row "PPGPEP Site do PPGPEP Programa de Pós-Graduação Profissional em Engenharia de Produção UFSCar · São Carlos Aula à noite — os três trabalham 08–18: atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: atende Universidade pública: atende aprovado 50% 4/5 001/2026 35 dias até 14 de set. · 25 vagas"':
        - cell "PPGPEP Site do PPGPEP Programa de Pós-Graduação Profissional em Engenharia de Produção":
          - text: PPGPEP
          - link "Site do PPGPEP":
            - /url: https://www.ppgpep.ufscar.br/pt-br
          - text: Programa de Pós-Graduação Profissional em Engenharia de Produção
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: atende"'
        - 'cell "Universidade pública: atende"'
        - cell "aprovado"
        - cell "50% 4/5"
        - cell "001/2026":
          - button "001/2026"
        - cell "35 dias até 14 de set. · 25 vagas"
      - 'row "CCMC Site do CCMC Programa de Pós-Graduação em Ciências de Computação e Matemática Computacional USP · São Carlos Aula à noite — os três trabalham 08–18: não verificado Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: atende Universidade pública: atende falta verificar 40% 3/5 — sem processo aberto"':
        - cell "CCMC Site do CCMC Programa de Pós-Graduação em Ciências de Computação e Matemática Computacional":
          - text: CCMC
          - link "Site do CCMC":
            - /url: https://www.icmc.usp.br/pos-graduacao
          - text: Programa de Pós-Graduação em Ciências de Computação e Matemática Computacional
        - cell "USP · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não verificado"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: atende"'
        - 'cell "Universidade pública: atende"'
        - cell "falta verificar"
        - cell "40% 3/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "MECAI Site do MECAI Mestrado Profissional em Matemática, Estatística e Computação Aplicadas à Indústria USP · São Carlos Aula à noite — os três trabalham 08–18: não verificado Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: atende Universidade pública: atende falta verificar 50% 4/5 — sem processo aberto"':
        - cell "MECAI Site do MECAI Mestrado Profissional em Matemática, Estatística e Computação Aplicadas à Indústria":
          - text: MECAI
          - link "Site do MECAI":
            - /url: https://www.icmc.usp.br/pos-graduacao/mecai
          - text: Mestrado Profissional em Matemática, Estatística e Computação Aplicadas à Indústria
        - cell "USP · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não verificado"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: atende"'
        - 'cell "Universidade pública: atende"'
        - cell "falta verificar"
        - cell "50% 4/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PPGAdS Site do PPGAdS Programa de Pós-Graduação Profissional em Administração e Sociedade UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não verificado Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: atende Universidade pública: atende falta verificar 50% 5/5 — sem processo aberto"':
        - cell "PPGAdS Site do PPGAdS Programa de Pós-Graduação Profissional em Administração e Sociedade":
          - text: PPGAdS
          - link "Site do PPGAdS":
            - /url: https://www.ppgads.ufscar.br/pt-br
          - text: Programa de Pós-Graduação Profissional em Administração e Sociedade
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não verificado"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: atende"'
        - 'cell "Universidade pública: atende"'
        - cell "falta verificar"
        - cell "50% 5/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PIPGEs Site do PIPGEs Programa Interinstitucional de Pós-Graduação em Estatística (UFSCar/USP) UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 40% 5/5 — sem processo aberto"':
        - cell "PIPGEs Site do PIPGEs Programa Interinstitucional de Pós-Graduação em Estatística (UFSCar/USP)":
          - text: PIPGEs
          - link "Site do PIPGEs":
            - /url: https://www.pipges.ufscar.br/pt-br
          - text: Programa Interinstitucional de Pós-Graduação em Estatística (UFSCar/USP)
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "40% 5/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PPGCC Site do PPGCC Programa de Pós-Graduação em Ciência da Computação UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 30% 5/5 02/2026 encerrado"':
        - cell "PPGCC Site do PPGCC Programa de Pós-Graduação em Ciência da Computação":
          - text: PPGCC
          - link "Site do PPGCC":
            - /url: https://www.ppgcc.ufscar.br/pt-br
          - text: Programa de Pós-Graduação em Ciência da Computação
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "30% 5/5"
        - cell "02/2026":
          - button "02/2026"
        - cell "encerrado"
      - 'row "PPGCI Site do PPGCI Programa de Pós-Graduação em Ciência da Informação UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 50% 5/5 — sem processo aberto"':
        - cell "PPGCI Site do PPGCI Programa de Pós-Graduação em Ciência da Informação":
          - text: PPGCI
          - link "Site do PPGCI":
            - /url: https://www.ppgci.ufscar.br/pt-br
          - text: Programa de Pós-Graduação em Ciência da Informação
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "50% 5/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PPGCTS Site do PPGCTS Programa de Pós-Graduação em Ciência, Tecnologia e Sociedade UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 70% 5/5 — sem processo aberto"':
        - cell "PPGCTS Site do PPGCTS Programa de Pós-Graduação em Ciência, Tecnologia e Sociedade":
          - text: PPGCTS
          - link "Site do PPGCTS":
            - /url: https://www.ppgcts.ufscar.br/pt-br
          - text: Programa de Pós-Graduação em Ciência, Tecnologia e Sociedade
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "70% 5/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PPGEE Site do PPGEE Programa de Pós-Graduação em Engenharia Elétrica UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 20% 5/5 — sem processo aberto"':
        - cell "PPGEE Site do PPGEE Programa de Pós-Graduação em Engenharia Elétrica":
          - text: PPGEE
          - link "Site do PPGEE":
            - /url: https://www.ppgee.ufscar.br/pt-br
          - text: Programa de Pós-Graduação em Engenharia Elétrica
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "20% 5/5"
        - cell "—"
        - cell "sem processo aberto"
      - 'row "PPGEP Site do PPGEP Programa de Pós-Graduação em Engenharia de Produção UFSCar · São Carlos Aula à noite — os três trabalham 08–18: não atende Presencial em São Carlos — mudar de cidade não está em questão: atende Sem mensalidade: não verificado Universidade pública: atende eliminado 60% 5/5 — sem processo aberto"':
        - cell "PPGEP Site do PPGEP Programa de Pós-Graduação em Engenharia de Produção":
          - text: PPGEP
          - link "Site do PPGEP":
            - /url: https://www.ppgep.ufscar.br/pt-br
          - text: Programa de Pós-Graduação em Engenharia de Produção
        - cell "UFSCar · São Carlos"
        - 'cell "Aula à noite — os três trabalham 08–18: não atende"'
        - 'cell "Presencial em São Carlos — mudar de cidade não está em questão: atende"'
        - 'cell "Sem mensalidade: não verificado"'
        - 'cell "Universidade pública: atende"'
        - cell "eliminado"
        - cell "60% 5/5"
        - cell "—"
        - cell "sem processo aberto"
  - paragraph:
    - text: Passe o mouse em qualquer ✓, ✗ ou ? para ver a evidência e a data em que o fato foi verificado. Um
    - strong: "?"
    - text: não é um "não" — é trabalho pendente.
  - heading "Detalhe por programa" [level=2]
  - tablist:
    - tab "PPGPEP aprovado"
    - tab "PPGCC eliminado" [selected]
  - tabpanel "PPGCC eliminado":
    - alert:
      - strong: "Eliminado: não há oferta noturna."
      - text: Nenhuma das 13 disciplinas deste semestre começa depois das 18:00. Com jornada 08:00–18:00, cursar este programa exigiria acordo com o empregador — não é questão de escolher a disciplina certa. Os números abaixo descrevem um programa que não é opção; ficam registrados porque foram verificados e porque explicam a eliminação.
    - heading "Programa de Pós-Graduação em Ciência da Computação" [level=2]
    - paragraph: UFSCar São Carlos · CAPES 5
    - list:
      - listitem: Aula à noite
      - listitem: Presencial em São Carlos
      - listitem: Gratuito
      - listitem: Público
    - text: Ofertas em 2026/2 13 grade publicada Conflitam com sua jornada 13/13 não há oferta noturna Docentes na AMPLN 9 a linha de IA/ML/PLN Vagas na AMPLN — último edital PPGCC · Mestrado 2027/1 previsto
    - paragraph: Inscrições — – — · 0 vagas
    - heading "Cronograma" [level=4]
    - list
    - separator
    - heading "Vagas" [level=4]
    - paragraph:
      - strong: 0 vagas
      - text: — o edital não as distribui por linha de pesquisa, então concorre-se a todas independentemente da linha escolhida.
    - separator
    - heading "Documentos exigidos" [level=4]
    - list
    - link "Página oficial do processo":
      - /url: https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado
    - heading "Grade semanal · 2026/2" [level=3]
    - paragraph: O programa publica apenas duas faixas, e nenhuma é noturna. Passe o mouse numa disciplina para ver docente, créditos, salas e idioma.
    - text: "Segunda Terça Quarta Quinta Sexta 08:00–12:00 CCO-310 Metodologia de Pesquisa Heloisa de Arruda Camargo CCO-129-7 Introdução à Computação de Alto Desempenho Hélio Crestana Guardia CCO-740 Reconhecimento de Padrões Alexandre Luís Magalhães Levada CCO-410 Aspectos Formais da Computação Wanderley Lopes de Souza CCO-04.1.02 Tópicos em Sistemas Distribuídos e Redes: Computação Ubíqua, Computação Pervasiva e Internet das Coisas Wanderley Lopes de Souza CCO-04.2.01 Segurança Cibernética Paulo Matias 14:00–18:00 CCO-741 Processamento Digital de Imagens Ricardo José Ferrari CCO-724 Aprendizado de Máquina Tiago Agostinho de Almeida CCO-00.2.01 Projeto e Análise de Algoritmos Alan Demétrius Baria Valejo CCO-00.2.03 Seminários II Fabiano Cutigi Ferrari CCO-220 Desenvolvimento de Software Orientado a Objetos Valter Vieira de Camargo CCO-03.2.02 Aprendizado Profundo para Reconhecimento Visual Jurandy Gomes de Almeida Junior CCO-03.2.01 Filtragem: Princípios e Aplicações Roberto Santos Inoue Faixa sombreada = sua jornada (08:00–18:00) · AMPLN BD CCH ES SAR SDARC VC"
    - heading "Linhas de pesquisa" [level=3]
    - paragraph: Passe o mouse na sigla para ver o nome oficial, os docentes e o que a linha significa.
    - table:
      - rowgroup:
        - row "Sigla Nome Docentes":
          - columnheader "Sigla"
          - columnheader "Nome"
          - columnheader "Docentes"
      - rowgroup:
        - row "AMPLN Aprendizado de Máquina e Processamento de Língua Natural 9":
          - cell "AMPLN"
          - cell "Aprendizado de Máquina e Processamento de Língua Natural"
          - cell "9"
        - row "BD Banco de Dados 5":
          - cell "BD"
          - cell "Banco de Dados"
          - cell "5"
        - row "CCH Computação Centrada no Humano 3":
          - cell "CCH"
          - cell "Computação Centrada no Humano"
          - cell "3"
        - row "ES Engenharia de Software 6":
          - cell "ES"
          - cell "Engenharia de Software"
          - cell "6"
        - row "SAR Sistemas de Automação e Robótica 4":
          - cell "SAR"
          - cell "Sistemas de Automação e Robótica"
          - cell "4"
        - row "SDARC Sistemas Distribuídos, Arquiteturas e Redes de Computadores 7":
          - cell "SDARC"
          - cell "Sistemas Distribuídos, Arquiteturas e Redes de Computadores"
          - cell "7"
        - row "VC Visão Computacional 7":
          - cell "VC"
          - cell "Visão Computacional"
          - cell "7"
  - heading "Monitoramento" [level=2]
  - paragraph: O coletor compara o TEXTO extraído, não os bytes — PDF regerado muda byte a byte dizendo a mesma coisa, e um monitor que grita à toa ninguém lê. PDF digitalizado, sem texto a extrair, cai para os bytes e diz que caiu.
  - paragraph: 19 fontes oficiais monitoradas · 2 catálogos · 2 com mudança
  - list:
    - listitem: Aluno especial processo seletivo há 3d
    - listitem: Calendário e disciplinas do semestre 2/2026 grade horária (PDF) há 3d
    - listitem: Disciplinas (ingressantes após jul/24) catálogo há 3d
    - listitem: Docentes docentes há 3d
    - listitem: Linhas de pesquisa página do programa há 3d
    - listitem: MECAI — edital vigente (002/2026) edital (PDF) há 3d
    - listitem: MECAI — ingresso e processo seletivo processo seletivo há 3d
    - listitem: MECAI — perguntas frequentes página do programa há 3d
    - listitem: Mestrado 2026/2 processo seletivo há 3d
    - listitem: PPGAdS — processos seletivos processo seletivo há 3d
    - listitem: PPGCC — página inicial página do programa há 3d
    - listitem: PPGCC — índice dos processos de mestrado processo seletivo há 3d
    - listitem: PPGPEP — Edital 001/2026 (ingresso 2027) edital (PDF) há 3d
    - listitem: PPGPEP — calendários e horários grade horária (PDF) há 3d
    - listitem: PPGPEP — disciplinas catálogo há 3d
    - listitem: PPGPEP — o programa página do programa há 3d
    - listitem: PPGPEP — processo seletivo processo seletivo há 3d
    - listitem: UFSCar ProPG — todos os programas de pós catálogo de programas há 3d
    - listitem: USP ICMC — pós-graduação catálogo de programas há 3d
  - text: Dados verificados em fontes oficiais da UFSCar — ver docs/research/. Campos não afirmados pela fonte ficam vazios, nunca preenchidos por inferência.
- alert
```

# Test source

```ts
  1   | import { expect, test, type Locator, type Page } from "@playwright/test";
  2   | 
  3   | /**
  4   |  * What only a browser can prove.
  5   |  *
  6   |  * The API tests already assert the numbers. These assert that a person opening
  7   |  * the page actually SEES them — that the data reaches the DOM, that the warning
  8   |  * about the site's misleading label is visible rather than merely present, and
  9   |  * that the weekly grid renders both time bands. Duplicating the API assertions
  10  |  * here would buy nothing and cost seconds per run.
  11  |  */
  12  | 
  13  | test.beforeEach(async ({ page }) => {
  14  |   /**
  15  |    * `networkidle` e não o default: um `hover()` disparado ANTES da hidratação é
  16  |    * perdido — o Base UI ainda não anexou os handlers —, e como o ponteiro não se
  17  |    * move de novo, o `expect` seguinte espera cinco segundos por uma tooltip que
  18  |    * nunca vai abrir. Isso passava por sorte no Next 15 e quebrou quatro testes no
  19  |    * 16, todos os que fazem hover no primeiro paint em vez de depois de um clique.
  20  |    */
  21  |   await page.goto("/", { waitUntil: "networkidle" });
  22  | });
  23  | 
  24  | /**
  25  |  * Faz hover até a tooltip abrir, e devolve o conteúdo dela.
  26  |  *
  27  |  * Um `hover()` único é uma corrida perdida: se ele acontece antes da hidratação,
  28  |  * o Base UI não tem handler para receber o evento, e como o ponteiro não se move
  29  |  * de novo a tooltip nunca abre — o `expect` seguinte espera cinco segundos por
  30  |  * algo que já foi decidido. Passava por sorte no Next 15 e quebrou quatro testes
  31  |  * no 16. Esperar mais não resolve; repetir o HOVER resolve.
  32  |  */
  33  | async function tooltipOf(page: Page, target: Locator): Promise<Locator> {
  34  |   const tip = page.locator('[data-slot="tooltip-content"]');
  35  |   await expect(async () => {
  36  |     await page.mouse.move(2, 2);
  37  |     await target.hover();
  38  |     await expect(tip.first()).toBeVisible({ timeout: 1000 });
  39  |   }).toPass({ timeout: 15_000 });
  40  |   return tip.first();
  41  | }
  42  | 
  43  | /** O PPGCC está atrás de uma aba porque está eliminado: quem abre a página
  44  |  *  precisa ver primeiro o que tem prazo. Os testes dele passam por aqui. */
  45  | async function openPpgcc(page: Page) {
  46  |   await page.getByRole("tab", { name: /PPGCC/ }).click();
  47  |   await expect(page.getByText(/Eliminado: não há oferta noturna/)).toBeVisible();
  48  | }
  49  | 
  50  | test("renders the search itself, not a single programme", async ({ page }) => {
  51  |   await expect(page.getByRole("heading", { name: "GradRadar", level: 1 })).toBeVisible();
  52  |   // The subtitle states the four eliminatory requirements. It used to name the
  53  |   // PPGCC — which is eliminated, and led the page with a dead end.
  54  |   await expect(page.getByText(/presencial em São Carlos e com aula à noite/)).toBeVisible();
  55  |   // Contagem por regex: ela cresce a cada varredura, e travar o número faria
  56  |   // este teste falhar por sucesso da pesquisa.
  57  |   await expect(page.getByText(/\d+ programas acompanhados/)).toBeVisible();
  58  | });
  59  | 
  60  | test("the open call leads the page, above everything else", async ({ page }) => {
  61  |   /**
  62  |    * The one thing here that is lost by not being seen in time. If this stops
  63  |    * being the first thing on the page, the project has failed at its only job.
  64  |    */
  65  |   const banner = page.locator("main > div").first();
  66  |   await expect(banner).toContainText("PPGPEP");
  67  |   await expect(banner).toContainText(/inscrições (abrem|abertas)/);
  68  |   await expect(banner).toContainText("14 de setembro de 2026");
  69  |   await expect(banner).toContainText("projeto de pesquisa");
  70  |   await expect(banner).toContainText(/dias? até fechar/);
  71  | });
  72  | 
  73  | test("seats that are not split by line say so instead of drawing empty bars", async ({ page }) => {
  74  |   const card = page.locator("div").filter({ hasText: /^PPGPEP · Mestrado/ }).first();
  75  |   await expect(
  76  |     page.getByText(/o edital não as distribui por linha de pesquisa/),
  77  |   ).toBeVisible();
  78  |   await expect(card).toBeVisible();
  79  | });
  80  | 
  81  | test("the schedule conflict is stated as a headline number", async ({ page }) => {
  82  |   await openPpgcc(page);
  83  |   const tile = page.locator("div", { hasText: /^Conflitam com sua jornada/ }).first();
  84  |   await expect(tile).toContainText("13/13");
  85  |   await expect(tile).toContainText("não há oferta noturna");
  86  | });
  87  | 
  88  | test("warns that the site label contradicts the real status", async ({ page }) => {
  89  |   await openPpgcc(page);
  90  |   // The behaviour the whole project exists for: the page must say the cycle is
  91  |   // closed even though the institution still calls it "Processo vigente".
  92  |   await expect(page.getByText(/encerrado/).first()).toBeVisible();
  93  |   const warning = page.getByText(/O site ainda rotula este processo como/);
  94  |   await expect(warning).toBeVisible();
  95  |   await expect(warning).toContainText("Processo vigente");
  96  | });
  97  | 
  98  | test("shows the admission timeline with dated stages", async ({ page }) => {
  99  |   await openPpgcc(page);
  100 |   await expect(page.getByText("CRONOGRAMA")).toBeVisible();
> 101 |   await expect(page.getByText(/Análise documental/)).toBeVisible();
      |                                                      ^ Error: expect(locator).toBeVisible() failed
  102 |   await expect(page.getByText(/Entrevista estruturada/)).toBeVisible();
  103 |   await expect(page.getByText(/13 de mai\. a 19 de mai\./)).toBeVisible();
  104 | });
  105 | 
  106 | test("the weekly grid renders both bands and neither is in the evening", async ({ page }) => {
  107 |   await openPpgcc(page);
  108 |   const grid = page.locator("section", { hasText: "Grade semanal" });
  109 |   await expect(grid.getByText("08:00–12:00")).toBeVisible();
  110 |   await expect(grid.getByText("14:00–18:00")).toBeVisible();
  111 |   // Five weekday columns, no Saturday and no evening row.
  112 |   for (const day of ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]) {
  113 |     await expect(grid.getByText(day, { exact: true })).toBeVisible();
  114 |   }
  115 |   await expect(grid.getByText("Sábado")).toHaveCount(0);
  116 | });
  117 | 
  118 | /** The offering card itself. Selecting on the trigger slot matters: a plain
  119 |  *  `div` with hasText also matches the day-column container, and hovering THAT
  120 |  *  opens whichever sibling happens to sit under the cursor. */
  121 | const card = (page: Page, code: string) =>
  122 |   page.locator('[data-slot="tooltip-trigger"]', { hasText: code });
  123 | 
  124 | test("the only AI offering of the term is visible with its professor", async ({ page }) => {
  125 |   await openPpgcc(page);
  126 |   const cell = card(page, "CCO-724");
  127 |   await expect(cell).toContainText("Aprendizado de Máquina");
  128 |   await expect(cell).toContainText("Tiago Agostinho de Almeida");
  129 | });
  130 | 
  131 | test("hovering an offering reveals the detail the card omits", async ({ page }) => {
  132 |   // The card shows code, name and professor; everything else lives in the
  133 |   // tooltip, so this is the only place that proves the rest reaches the user.
  134 |   await openPpgcc(page);
  135 |   // Base UI does not set role="tooltip" — the popup is identified by its slot.
  136 |   const tip = await tooltipOf(page, card(page, "CCO-724"));
  137 |   await expect(tip).toContainText("Machine Learning"); // the English name
  138 |   await expect(tip).toContainText("AMPLN");
  139 |   await expect(tip).toContainText("14:00–18:00");
  140 |   // Two rooms, because the same class runs at both campuses — and this one
  141 |   // ORIGINATES in Sorocaba.
  142 |   await expect(tip).toContainText("CCGT-1001");
  143 |   await expect(tip).toContainText("Conflita integralmente");
  144 | });
  145 | 
  146 | test("every research-line acronym explains itself on hover", async ({ page }) => {
  147 |   // The acronyms are opaque to anyone outside computing — and three people will
  148 |   // use this. Each must carry the official name, a plain gloss, and what the
  149 |   // line actually taught.
  150 |   await openPpgcc(page);
  151 |   const row = page.getByRole("row", { name: /AMPLN/ });
  152 |   const tip = await tooltipOf(page, row.getByText("AMPLN"));
  153 |   await expect(tip).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  154 |   await expect(tip).toContainText("Ensinar computadores a aprender padrões");
  155 |   await expect(tip).toContainText("Docentes");
  156 | });
  157 | 
  158 | test("a line with no offering this term says so instead of showing nothing", async ({ page }) => {
  159 |   // BD taught nothing in 2026/2. An empty field would read as missing data;
  160 |   // the absence is itself the information.
  161 |   await openPpgcc(page);
  162 |   const row = page.getByRole("row", { name: /Banco de Dados/ });
  163 |   const tip = await tooltipOf(page, row.getByText("BD", { exact: true }));
  164 |   await expect(tip).toContainText("nenhuma disciplina ofertada");
  165 | });
  166 | 
  167 | test("research lines are listed with their faculty counts", async ({ page }) => {
  168 |   await openPpgcc(page);
  169 |   const row = page.getByRole("row", { name: /AMPLN/ });
  170 |   await expect(row).toContainText("Aprendizado de Máquina e Processamento de Língua Natural");
  171 |   await expect(row).toContainText("9");
  172 | });
  173 | 
  174 | test("the eliminated programme is one click away, never the default", async ({ page }) => {
  175 |   /**
  176 |    * A regra que estrutura a página: o programa que não serve não pode ser a
  177 |    * primeira coisa que alguém lê. Antes disso, era.
  178 |    */
  179 |   await expect(page.getByRole("tab", { name: /PPGPEP/ })).toHaveAttribute("aria-selected", "true");
  180 |   await expect(page.getByText(/Aprendizado de Máquina e Processamento/)).toHaveCount(0);
  181 | 
  182 |   await openPpgcc(page);
  183 |   await expect(page.getByText(/Aprendizado de Máquina e Processamento/).first()).toBeVisible();
  184 | });
  185 | 
  186 | test("the edital is shown as actions, not as a wall of dates", async ({ page }) => {
  187 |   /**
  188 |    * A informação decisiva do edital não é uma data: é que o projeto de pesquisa
  189 |    * precisa estar escrito ANTES de a inscrição abrir. Se isso não estiver
  190 |    * visível, a página informa sem servir para nada.
  191 |    */
  192 |   const steps = page.getByText("O que fazer, em ordem");
  193 |   await expect(steps).toBeVisible();
  194 |   await expect(page.getByText(/três das quatro etapas acontecem/)).toBeVisible();
  195 | 
  196 |   // O primeiro passo vem aberto — é o que consome as quatro semanas.
  197 |   await expect(page.getByText(/É a única coisa avaliada/)).toBeVisible();
  198 | 
  199 |   const anexo = page.getByRole("button", { name: /declaração de vínculo/ });
  200 |   await anexo.click();
  201 |   await expect(page.getByText(/Anexo II/)).toBeVisible();
```