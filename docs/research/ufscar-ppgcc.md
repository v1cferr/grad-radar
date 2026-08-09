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

**This is the single most important finding of F1A** and it is a negative one: the cycle page contains
*links and no facts*. Dates, seat counts, required documents, stages and fees are **not in the HTML** — they
are inside the edital PDF behind SEI. See [Modeling implications](#modeling-implications).

The existence of `Resultado etapa 0..3` establishes that the process has **at least four ordered, numbered
stages** producing published results. The word `retificada` establishes that **published documents get
revised mid-cycle** — versioning is a requirement, not a nicety.

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

## Courses, timetable, work compatibility

**Nothing verified.** No course catalogue, no timetable and no attendance policy was located during this pass.
This is the largest gap, and it is the gap that matters most for the project's core question — whether a
program is compatible with a full-time job.

## Scholarships

**Nothing verified.** The site navigation includes a scholarships section under `Programa`, not yet fetched.

## Tuition

**Not stated anywhere on the pages consulted.** Brazilian federal universities do not charge tuition for
academic graduate programs, but *this project must not encode inference as fact* — it stays unresolved until
an official page states it.

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

**8. Unknown must be representable and distinct from absent.** Tuition, timetable and credit transfer are all
unknown-not-false. A nullable column silently reads as "no". Consider an explicit unknown marker or a
`fact + source + confidence` shape for the fields that drive scoring.

---

## Unknown / unresolved

Ordered by how much each blocks the project's core question.

1. **Course timetables and attendance policy** — the single most decision-relevant gap. Blocks the
   work-compatibility dimension entirely.
2. **Whether aluno especial credits transfer** to the regular program. Assumed in this project's docs;
   *not stated* by the source.
3. **Tuition-free status** — near-certain by Brazilian law, unverified on-site.
4. **2026/2 cycle specifics** — dates, seats per line, documents, fees, stages. Inside the edital PDF,
   not yet retrieved.
5. **English proficiency requirement** — not stated on any page consulted.
6. **Prior advisor contact** — whether required or merely recommended.
7. **Scholarships** — availability, source (CAPES/CNPq/FAPESP), and whether they forbid employment.
8. **Research line descriptions** — the overview page has names only.
9. **Laboratories** — several are inferable from faculty links (`biomal`, `aloc`, `advanse`, `laris`,
   `bipgroup`, `uxleris`, `inag`, `lapes`) but none were fetched or verified as PPGCC-affiliated labs.
10. **Seat counts per research line** — the search layer suggested AMPLN receives an allocation, but this was
    not confirmed against an official page and is therefore excluded from the tables above.

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
| <https://www.dc.ufscar.br/p%C3%B3s-gradua%C3%A7%C3%A3o/ppgcc> | department affiliation |

Not consulted yet: scholarships page, course catalogue, internal regulations
(*Regimento Interno e Normas Complementares*), the edital PDFs themselves, and any laboratory page.
