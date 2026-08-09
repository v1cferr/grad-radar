# PPGCC/UFSCar — domain discovery

**Phase:** F1A · **Researched:** 2026-08-08 · **Method:** official sources only (`ppgcc.ufscar.br`, `dc.ufscar.br`)

This document exists to force domain discovery **before** schema design. Every factual statement carries the
URL it came from. Anything not stated by an official source is listed under
[Unknown / unresolved](#unknown--unresolved), never guessed.

---

## Program

| Field | Value | Source |
| --- | --- | --- |
| Official name | Programa de Pós-Graduação em Ciência da Computação (PPGCC) | [ppgcc.ufscar.br/pt-br](https://www.ppgcc.ufscar.br/pt-br) |
| Institution | Universidade Federal de São Carlos (UFSCar) | idem |
| Address | Rodovia Washington Luís, km 235 — São Carlos/SP | idem |
| Department | Departamento de Computação (DC) | [dc.ufscar.br/pós-graduação/ppgcc](https://www.dc.ufscar.br/p%C3%B3s-gradua%C3%A7%C3%A3o/ppgcc) |
| CAPES rating | Concept **5** (Avaliação Quadrienal) | [ppgcc.ufscar.br/pt-br](https://www.ppgcc.ufscar.br/pt-br) |

### Academic levels offered

Mestrado · Doutorado · Doutorado Direto · Pós-Doutorado · Aluno Especial · Graduação-Mestrado
— [ppgcc.ufscar.br/pt-br](https://www.ppgcc.ufscar.br/pt-br)

Note that **"Aluno Especial" and "Graduação-Mestrado" are listed as peers of Mestrado/Doutorado** in the
program's own navigation. They are entry modes, not degree levels — the model must not collapse the two
concepts into one enum.

---

## Research lines

Seven lines, verbatim from [`/pt-br/programa/linhas-de-pesquisa`](https://www.ppgcc.ufscar.br/pt-br/programa/linhas-de-pesquisa):

| Acronym | Name (verbatim) |
| --- | --- |
| **AMPLN** | Aprendizado de Máquina e Processamento de Língua Natural |
| BD | Banco de Dados |
| CCH | Computação Centrada no Humano |
| ES | Engenharia de Software |
| SAR | Sistemas de Automação e Robótica |
| SDARC | Sistemas Distribuídos, Arquiteturas e Redes de Computadores |
| VC | Visão Computacional |

The overview page lists **names only** — no descriptions, no scope statements, no faculty. Per-line detail,
if it exists, lives elsewhere.

**AMPLN is the primary line of interest.** It is the only one whose name names AI directly. But see
[Modeling implications](#modeling-implications): line name alone is a poor relevance signal, and VC/ES/BD
contain AI-adjacent work that a name-based filter would miss.

---

## Faculty

41 faculty listed at [`/pt-br/programa/docentes`](https://www.ppgcc.ufscar.br/pt-br/programa/docentes), each
with affiliation status, research line, email and a link (Lattes, lab, or personal page).

### AMPLN — the AI/ML/NLP line (9 members)

| Name | Status | Link |
| --- | --- | --- |
| Alan Demétrius Baria Valejo | Permanent | [www2.dc.ufscar.br/~alanvalejo](http://www2.dc.ufscar.br/~alanvalejo/) |
| Helena de Medeiros Caseli | Permanent | [Lattes 6608582057810385](http://lattes.cnpq.br/6608582057810385) |
| Heloisa de Arruda Camargo | Permanent | [Lattes 0487231065057783](http://lattes.cnpq.br/0487231065057783) |
| Mário César San Felice | Permanent | [aloc.ufscar.br/felice](https://www.aloc.ufscar.br/felice/) |
| Murilo Coelho Naldi | Permanent | [Lattes 7924553462118511](http://lattes.cnpq.br/7924553462118511) |
| Ricardo Augusto Souza Fernandes | Permanent | [liaa2.webnode.com](https://liaa2.webnode.com/) |
| Ricardo Cerri | Permanent | [biomal.ufscar.br](http://www.biomal.ufscar.br/) |
| Tiago Agostinho de Almeida | Permanent | [servidores.ufscar.br/talmeida](https://www.servidores.ufscar.br/talmeida/) |
| Diego Furtado Silva | **Collaborator** | [sites.google.com/view/diegofsilva](https://sites.google.com/view/diegofsilva) |

### Distribution across all lines

| Line | Count |
| --- | --- |
| AMPLN | 9 |
| VC | 7 |
| SDARC | 6 |
| ES | 6 |
| BD | 5 |
| SAR | 4 |
| CCH | 3 |
| *(none listed)* | 1 |

### Structural facts the model must accommodate

- **Affiliation status is a real enum with three values**: `Permanent`, `Collaborator`, `Senior Permanent`
  (the last for Marilde Terezinha Prado Santos and Wanderley Lopes de Souza). This matters directly: CAPES
  rules generally restrict who may advise, so status is not decoration.
- **A faculty member can belong to more than one line.** Auri Marcelo Rizzo Vincenzi is listed under **BD and
  ES**. A single `research_line_id` foreign key would lose this — the relation is M:N.
- **A faculty member can have no line.** Paulo Estevão Cruvinel has status Collaborator and no line listed.
  The relation must tolerate zero.
- **Links are heterogeneous by nature**: Lattes URLs, lab sites, personal sites, `linktr.ee`, Google Sites. A
  single `lattes_url` column would discard most of them. This is a 1:N "links" relation, or a typed set.
- **Email is published but obfuscated** as `name(at)ufscar.br`. Storing it requires a normalisation decision;
  storing it at all requires a privacy decision.
- **External affiliation exists**: Diego Furtado Silva's email is `@icmc.usp.br` and Paulo Cruvinel's is
  `@embrapa.br`. "Faculty of PPGCC" is not the same as "employed by UFSCar" — relevant once ICMC-USP enters
  and the same person may appear in both programs.

---

## Admission

### Regular (Mestrado)

There is a **currently open process**: *"Processo seletivo do Mestrado para o 2º Semestre de 2026"*, labelled
`Processo vigente` — [`/pt-br/processo-seletivo/mestrado`](https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado)

Past cycles are archived under `/pt-br/processo-seletivo/mestrado/editais-anteriores/<year>-<n>o-semestre`,
which confirms **one cycle per semester** and a stable, predictable URL shape.

The [2026/1 cycle page](https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado/editais-anteriores/2026-1o-semestre)
carries these artifacts:

- `Edital 01/2026` — **PDF served through the SEI system**
- `Link para o processo SEI`
- `Comissões de avaliação por linha de pesquisa (retificada)` — note **"retificada"**: the document was revised
- `Resultado etapa 0 - Inscrições recebidas`
- `Resultado etapa 1`, `Resultado etapa 2`, `Resultado etapa 3`

The cycle page contains *links and no facts*: dates, seat counts, documents, stages and fees are **not in the
HTML** — they live inside the edital PDF behind SEI. The word `retificada` on one artifact establishes that
**published documents get revised mid-cycle** — versioning is a requirement, not a nicety.

### Edital 02/2026 — retrieved and parsed

The SEI PDF **is** machine-retrievable. Contents:

| Field | Value |
| --- | --- |
| Application period | **19/03/2026 to 26/04/2026** |
| Total positions | **23** — *"Número de vagas oferecidas neste processo seletivo: 23 (vinte e três)"* |
| Stage 1 — Documentary analysis | 13–19/05/2026 · results 24/06 |
| Stage 2 — Structured interview | 07–20/06/2026 · results 24/06 |
| Application fee | not mentioned |
| Prior advisor contact | **not required** |

Seats per research line:

| AMPLN | VC | SDARC | SAR | BD | ES | CCH |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 7 | 7 | 2 | 1 | 1 | 1 |

Affirmative action reserves **20%** for Black/mixed-race candidates, **5%** for candidates with disabilities,
and **1 seat** for Indigenous candidates.

> A first reading of this PDF reported "21 total". The per-line figures sum to 23, and re-reading the document
> confirmed *"23 (vinte e três)"*. The contradiction was caught by the seeded database, not by a human — which
> is a small argument for storing seats per line rather than as one number on the cycle.

Required documents: diploma or completion certificate, official transcript, Lattes CV (Brazilian applicants),
identity documents, **presentation letter (max. 800 words)**, proof of address, optional proficiency
certificates. Submission is via **Google Form**.

English proficiency is **not** an entry requirement:

> "O aluno que vier a ser aprovado […] deverá submeter-se ao Exame de Proficiência em Língua Estrangeira"

— i.e. it is required *after* admission, before qualification. Modelling it as an application requirement
would be wrong.

### "Processo vigente" does not mean "applications open"

The 2026/2 cycle is labelled `Processo vigente`, yet its application window closed **26/04/2026** and results
for all stages are already published. As of this research (08/08/2026) **nothing is open for application**.

A scraper reading the site label would report a false opportunity. `AdmissionCycle` therefore needs a status
derived from **dates**, not from the site's wording, and must distinguish *applications open* from *in
progress* from *concluded*.

### Aluno especial

From [`/pt-br/processo-seletivo/aluno-especial`](https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/aluno-especial):

> "O PPGCC seleciona semestralmente graduandos e graduados para cursarem disciplinas isoladas da pós-graduação."

- **Frequency:** semestral.
- **Timing:** *"O período de inscrições e divulgação dos candidatos selecionados ocorrem de acordo com o
  calendário acadêmico que é divulgado semestralmente."* — governed by the **academic calendar**, not by an
  edital. Mechanically different from the regular process.
- **Eligibility:** undergraduates in their penultimate year or later with good standing, or graduates in
  computing or related fields.
- **Process:** online form only.
- **Progression:** *"após graduar-se, poderá tornar-se aluno regular do PPGCC, mediante aprovação no processo
  de seleção."* — becoming a regular student still requires passing selection. **The page does not state that
  credits transfer.**

That last point corrects an assumption carried in this project's own docs: credit reuse is a *hypothesis*, not
a verified fact. It is listed as unresolved below.

---

## Courses

The catalogue lists **43 disciplines** at
[`/pt-br/programa/estrutura-curricular/disciplinas-do-programa_apos_jul_24`](https://www.ppgcc.ufscar.br/pt-br/programa/estrutura-curricular/disciplinas-do-programa_apos_jul_24)
(for students entering after July 2024; a separate catalogue exists for earlier entrants), organised into four
groups:

| Group | Theme |
| --- | --- |
| I | Teoria da Computação, Análise de Algoritmos e Complexidade |
| II | Metodologia e Técnicas de Computação — with explicit **Artificial Intelligence** and **Computer Vision** sub-groups |
| III | Sistemas de Computação |
| IV | Qualificação Discente |

Most disciplines carry **8 credits**; a few in Group IV carry 4. The catalogue page shows **code, name and
credits only** — no professor, no schedule, no syllabus link.

Two catalogues coexist (`_apos_jul_24` and `_ate_jul_24`), so **curriculum version is a real dimension**: the
set of valid disciplines depends on when the student entered.

## Timetable and work compatibility

**This is the decisive finding of F1A.**

The semester offering is published as
["Calendário e disciplinas do semestre 2 2026"](https://www.ppgcc.ufscar.br/pt-br/programa/estrutura-curricular/disciplina-do-semestre)
— a page that **302-redirects to a PDF in SEI**. The PDF is a weekly grid, and it carries far more than the
catalogue does. Per offering:

- code and name (Portuguese **and** English)
- **Docente ministrante** — the teaching professor
- **Linha** — `Básica` or `Específica <LINE>`
- **Tipo** — group I–IV
- **Local no campus de origem** — e.g. `São Carlos: Auditório`, `São Carlos: LE 6`, `São Carlos: Sala 2`
- **Local no outro campus** — e.g. `Sorocaba - CCGT-1001`
- **Idioma** — `Português` or `Inglês`

### The two time slots

The grid has **exactly two time bands**, across Monday–Friday:

```
08h - 12h
14h - 18h
```

**There is no evening offering.** Both bands fall squarely inside a commercial working day.

This answers the question that motivates the whole project, and the answer is negative: **PPGCC/UFSCar
disciplines cannot be attended alongside a standard 8-hour commercial job without employer accommodation.**
The constraint is structural — not a matter of picking the right discipline.

### Semester 2/2026 offering

13 offerings: 4 `Básica` and 9 `Específica` (SDARC 3, VC 3, AMPLN 1, ES 1, SAR 1). Language: 7 in Portuguese,
6 in English.

**AMPLN — the line of interest — has exactly one offering this semester:** `CCO-724 — Aprendizado de Máquina
(Machine Learning)`, taught by **Tiago Agostinho de Almeida**.

Sampled offerings, verbatim:

| Code | Discipline | Professor | Line | Language |
| --- | --- | --- | --- | --- |
| CCO-724 | Aprendizado de Máquina | Tiago Agostinho de Almeida | Específica AMPLN | *(see PDF)* |
| CCO-310 | Metodologia de Pesquisa | Heloisa de Arruda Camargo | Básica | Inglês |
| CCO-741 | Processamento Digital de Imagens | Ricardo José Ferrari | Específica VC | *(see PDF)* |
| CCO-00.2.01 | Projeto e Análise de Algoritmos | Alan Demétrius Baria Valejo | Básica | *(see PDF)* |
| CCO-220 | Desenvolvimento de Software Orientado a Objetos | Valter Vieira de Camargo | Específica ES | *(see PDF)* |
| CCO-410 | Aspectos Formais da Computação | Wanderley Lopes de Souza | Básica | Português |

### Dual-campus delivery

Every offering lists a room at **both** São Carlos and Sorocaba (`CCGT-1001`). The same discipline runs
simultaneously at two campuses. Whether this is video-linked or duplicated is not stated, but it means an
offering has **more than one location**, which a single `room` column cannot express.

## Scholarships

The edital states plainly:

> "A classificação no processo seletivo não implica concessão de bolsa"

Scholarship criteria are handled separately from admission. Funding agencies, values and whether employment is
permitted: **not stated** in the edital.

## Tuition

**Not stated anywhere on the pages consulted.** Brazilian federal universities do not charge tuition for
academic graduate programs, but *this project must not encode inference as fact* — it stays unresolved until
an official page states it.

---

## Internal regulation (Regimento)

Retrieved from [`regimento.pdf`](https://www.ppgcc.ufscar.br/pt-br/assets/arquivos/regimentos-e-normas/regimento.pdf)
— the document that settles three of the open questions.

**Credits from aluno especial DO transfer** — Art. 21, parágrafo único, verbatim:

> "A critério da CPG, poderão ser reconhecidas **todas** as disciplinas cursadas no próprio Programa, como
> Aluno Especial, desde que cursadas no máximo **dois anos** antes da matrícula como aluno regular no curso."

Two conditions matter and neither was visible on the admission pages: it is **at the CPG's discretion**, and
there is a **two-year window**. Disciplines taken at *another* institution are capped at 40% of the required
credits (Art. 21, caput); disciplines taken *here* as aluno especial have no such cap.

This resolves the assumption carried in `MOTIVACOES.md` — but qualifies it. "Créditos aproveitam" is true only
inside two years and only if the CPG agrees.

**Credits and deadlines** — Art. 19:

> "Para a conclusão do curso de Mestrado serão exigidos 100 (cem) créditos, sendo 50 (cinqüenta) créditos em
> disciplinas e 50 (cinqüenta) créditos integralizados com a homologação pela CPG de aprovação na defesa da
> Dissertação."
>
> "A integralização dos créditos em disciplinas deve ser feita no prazo máximo de 18 (dezoito) meses, contados
> a partir do ingresso como aluno regular."

One credit = 15 hours. So **50 credits in disciplines ≈ 750 hours**, and since most disciplines carry 8
credits, that is **roughly 6–7 disciplines inside 18 months** — about two per semester, every semester, all of
them inside the 08–12 / 14–18 bands. This turns the timetable finding from a scheduling annoyance into an
arithmetic problem.

**Aluno especial for a graduate** — Art. 13, §2º: open to a holder of a higher-education diploma not enrolled
in the programme, at the responsible lecturer's discretion, for candidates whose interest is
*"aprimoramento profissional"*. That is the applicable route here; §3º (Aluno Especial **Graduando**) applies
to undergraduates and additionally requires a letter of intent from an advisor.

**Attendance:** the word *frequência* does not appear in the regimento. Grading is per-discipline, by the
lecturer (Art. 22, levels A–E). So the minimum-attendance rule is **still unresolved** — but the semester grid
carries a note that does bear on it: *"Todas as avaliações são integralmente presenciais no departamento."*

---

## Modeling implications

What the discovered reality demands of the schema. These are the decisions F1B should implement.

**1. The authoritative content is a PDF, not a page.** The cycle page is a link hub; the facts live in
`Edital 01/2026` behind SEI. Therefore provenance cannot be a URL column on the fact — a fact must point to a
*retrieved document*. `Source` (a monitored location) and `SourceSnapshot` (what it contained at a moment,
with hash and retrieval time) must be separate from the first migration, and `source_type` must distinguish
`edital_pdf` from `admission_page`.

**2. Documents get revised in flight.** `Comissões de avaliação ... (retificada)` proves it. A notice needs
versions, and a version needs to be comparable to its predecessor — which is what F5 will diff.

**3. Cycles are temporal, programs are not.** `2026-1o-semestre`, `2026-2o-semestre` are archived siblings of
one program. `AdmissionCycle` keyed by (program, year, semester, entry type) with its own status
(`open` / `closed` / `expected`) — and `expected` matters, because the project's stated principle is
recognising a *future* window rather than chasing the first open one.

**4. Entry mode ≠ degree level.** The program lists Mestrado, Doutorado, Doutorado Direto, Pós-Doutorado,
Aluno Especial and Graduação-Mestrado as peers. `degree_level` (master/doctorate) and `entry_mode`
(regular/special-student/direct/graduation-track) are two axes, and aluno especial has different mechanics
entirely (academic calendar, no edital, online form).

**5. Faculty ↔ research line is M:N and optional.** Proven by Auri Vincenzi (two lines) and Paulo Cruvinel
(none). Affiliation status is a first-class enum, not a boolean, because it likely governs advising
eligibility.

**6. Faculty links are a set, not a column.** Lattes, lab, personal site, linktr.ee. Model as typed links so
the lab URL survives — the lab is the entity that reveals *actual research activity*, which is what
distinguishes a program with an AI line from a program doing AI.

**7. Line name is a weak relevance signal.** Only AMPLN names AI, yet VC is computer vision, ES has
AI-for-testing work, and BD has data-centric overlap. Scoring must reach the faculty/lab/publication level,
not stop at the line. This is exactly the traceability chain the project needs:
`program → line → faculty → lab → project/publication → source`.

**8. Unknown must be representable and distinct from absent.** Tuition and credit transfer are
unknown-not-false. A nullable column silently reads as "no". Consider an explicit unknown marker or a
`fact + source + confidence` shape for the fields that drive scoring.

**9. Cycle status must be derived from dates, never from the site's label.** `Processo vigente` currently
labels a cycle whose applications closed three months ago. A `status` column populated from page wording
would make the system announce opportunities that do not exist — the exact failure the project is built to
prevent.

**10. Discipline ≠ offering, and the line lives on the offering.** The catalogue gives a discipline a code,
name and credits. Everything decision-relevant — professor, weekday, time band, room, language, and whether
it counts as `Básica` or `Específica <LINE>` — belongs to a **semester offering**. `CCO-724` is not
"an AMPLN discipline"; it is *offered as* AMPLN-specific in 2026/2.

**11. An offering has two locations, not one.** Every row lists a São Carlos room *and* a Sorocaba room. A
scalar `room` column is wrong from day one.

**12. Language of instruction is a real attribute** — 6 of 13 offerings are taught in English. It was not in
the original entity list and matters for candidate fit.

**13. Time is a coarse band, not a timestamp.** Only `08h - 12h` and `14h - 18h` exist. Weekday + band is a
faithful and sufficient representation; modelling recurrence rules would be overengineering for a domain
whose real granularity is two slots. But the band must be **comparable to a work schedule** — that comparison
is the product's whole point.

**14. Curriculum version is a dimension.** Two catalogues coexist (`_apos_jul_24`, `_ate_jul_24`), keyed by
entry date. Which disciplines are valid depends on when the student entered.

---

## Unknown / unresolved

Ordered by how much each blocks the project's core question. Items resolved in this pass are struck through.

1. **Attendance policy** — the regimento does not use the word *frequência* at all; grading is left to each
   lecturer (Art. 22). The only nearby fact is the grid's note that **all assessments are fully in person at
   the department**. Whether a minimum attendance exists remains unresolved, and it is the last question
   standing between the timetable finding and a decision.
2. **Tuition-free status** — near-certain by Brazilian law, unverified on-site.
4. **Scholarship detail** — the edital says classification does not imply a scholarship, but funding source
   (CAPES/CNPq/FAPESP), value, and whether employment is permitted are all unstated. Decisive for anyone
   holding a job.
5. **Research line descriptions** — the overview page has names only.
6. **Laboratories** — several are inferable from faculty links (`biomal`, `aloc`, `advanse`, `laris`,
   `bipgroup`, `uxleris`, `inag`, `lapes`) but none were fetched or verified as PPGCC-affiliated labs.
7. **Aluno especial timetable** — whether special students attend the same grid (likely, but unstated) and
   how many disciplines they may take.
8. **Internal regulations** — `regimento.pdf` was located but not read; it likely settles credits required,
   duration limits and the credit-transfer question.
9. **Next cycle (2027/1)** — no page yet. Based on the archive URL pattern and the observed March–April
   window, a cycle is *expected* rather than known.

Resolved so far: ~~course timetables~~ · ~~2026/2 cycle specifics~~ · ~~English proficiency~~ ·
~~prior advisor contact~~ · ~~seat counts per line~~ · ~~aluno especial credit transfer~~ ·
~~credits required~~ · ~~time limit to complete disciplines~~

---

## Sources consulted

| URL | What it established |
| --- | --- |
| <https://www.ppgcc.ufscar.br/pt-br> | program identity, levels, campus, CAPES 5, navigation |
| <https://www.ppgcc.ufscar.br/pt-br/programa/linhas-de-pesquisa> | the seven lines, verbatim |
| <https://www.ppgcc.ufscar.br/pt-br/programa/docentes> | 41 faculty, status, lines, links |
| <https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado> | open 2026/2 cycle, archive URL shape |
| <https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado/editais-anteriores/2026-1o-semestre> | cycle artifacts, SEI/PDF pattern, stage count, "retificada" |
| <https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/aluno-especial> | semestral special-student intake, eligibility, calendar-driven |
| <https://www.ppgcc.ufscar.br/pt-br/processo-seletivo/mestrado/2026-2o-semestre> | Edital 02/2026 + links SEI de todas as etapas |
| SEI — Edital 02/2026 (PDF) | datas, 21 vagas por linha, etapas, documentos, proficiência, bolsa |
| <https://www.ppgcc.ufscar.br/pt-br/programa/estrutura-curricular> | hub do currículo; dois catálogos por data de ingresso |
| <https://www.ppgcc.ufscar.br/pt-br/programa/estrutura-curricular/disciplinas-do-programa_apos_jul_24> | 43 disciplinas, códigos, créditos, grupos I–IV |
| SEI — "Calendário e disciplinas do semestre 2 2026" (PDF, via redirect 302) | **a grade horária**: dia, faixa, docente, linha, salas nos dois campi, idioma |
| <https://www.dc.ufscar.br/p%C3%B3s-gradua%C3%A7%C3%A3o/ppgcc> | department affiliation |

Not consulted yet: scholarships page, internal regulations
([`regimento.pdf`](https://www.ppgcc.ufscar.br/pt-br/assets/arquivos/regimentos-e-normas/regimento.pdf)),
and any laboratory page.
