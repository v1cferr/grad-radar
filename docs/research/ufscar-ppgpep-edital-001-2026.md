# PPGPEP/UFSCar — Edital 001/2026, ingresso em 2027

**Este é o único processo seletivo aberto que atende aos quatro requisitos eliminatórios**
([`../GOAL.md`](../GOAL.md)). Publicado em 05/08/2026; as inscrições abrem em **20/08/2026** e
fecham em **14/09/2026**.

Fonte: `https://www.ppgpep.ufscar.br/en/assets/arquivos/edital-ppgpep-2026.pdf`
(18 páginas), linkado em `https://www.ppgpep.ufscar.br/pt-br/processo-seletivo`.

> **O PDF é digitalizado e não tem camada de texto.** `pdftotext` devolve zero linhas; foi preciso
> renderizar as páginas com `pdftoppm` e ler as imagens. Isso não é uma curiosidade — expôs um bug
> real no coletor, descrito no fim deste documento.

---

## O essencial

| | |
| --- | --- |
| Programa | Mestrado **Profissional** em Engenharia de Produção |
| Vagas | **25** — 17 ampla concorrência + 8 de ações afirmativas |
| Ações afirmativas | 5 negros (pretos e pardos), 1 indígena, 2 PcD |
| Distribuição por linha | **Não há.** Edital 3.6: as vagas não são distribuídas por linha de pesquisa |
| Bolsas | **Não há.** Edital 11.3: o programa não dispõe de bolsas de CAPES/CNPq |
| Assinatura | São Carlos, 05/08/2026 — Profa. Dra. Fabiane Letícia Lizarelli |

Sem bolsa é irrelevante aqui: os três mantêm o vínculo com a FAI. Um mestrado profissional noturno
sem bolsa é exatamente o formato compatível com quem trabalha — e é o motivo de ele existir.

### Linhas de pesquisa (três, não quatro)

| Sigla | Nome | O que é |
| --- | --- | --- |
| PCsP | Planejamento e Controle de Sistemas Produtivos | capacidade, estoques, programação, operação |
| GQ | Gestão da Qualidade | medir, controlar e melhorar qualidade |
| **TOTI** | Trabalho, Organizações, Tecnologia e Inovação | adoção de tecnologia e inovação nas organizações |

**TOTI é a linha relevante.** É onde "adoção institucional de IA" — o trabalho que o Victor já faz na
FAI — cabe como objeto de pesquisa. Ainda não foi verificada a aderência real: docentes e projetos da
linha continuam por levantar.

---

## Cronograma (Anexo I)

| Etapa | Data |
| --- | --- |
| Divulgação do edital | 05/08/2026 |
| Recursos / impugnação do edital | 05/08 a 15/08/2026 |
| Análise dos recursos | 17/08 a 18/08/2026 |
| Resultado dos recursos | 19/08/2026 |
| **Inscrições** | **20/08/2026 a 14/09/2026** |
| Lista preliminar de inscrições | 18/09/2026 |
| Recursos ao indeferimento | 19/09 a 28/09/2026 |
| Lista definitiva de inscrições | 02/10/2026 |
| Comissão de Seleção — preliminar | 19/10/2026 |
| Recursos à composição da comissão | 20/10 a 29/10/2026 |
| Comissão de Seleção — definitiva | 30/10/2026 |
| **Etapa 1 — Avaliação do Projeto de Pesquisa** (notas) | 06/11/2026 |
| Recursos da etapa 1 | 07/11 a 16/11/2026 |
| Resultado dos recursos | 18/11/2026 |
| Datas e horários da defesa | 19/11/2026 |
| **Etapa 2 — Defesa do Projeto de Pesquisa** | 23/11 a 01/12/2026 |
| Notas da etapa 2 e nota final | 04/12/2026 |
| Recursos finais | 05/12 a 15/12/2026 |
| **Resultados definitivos** | 18/12/2026 |

O processo é longo, mas a única data que não perdoa é **14/09/2026**.

## O que a seleção realmente cobra

Duas etapas, e **as duas são sobre o projeto de pesquisa** — não há prova escrita de conteúdo, não há
exame de proficiência eliminatório na etapa 1. Etapa 1 avalia o projeto submetido; etapa 2 é a defesa
oral dele diante da comissão (24 membros no total, distribuídos em bancas).

A consequência prática é que **o esforço é anterior à inscrição**: quem chega em 20/08 sem projeto
escrito não tem o que submeter. Restam cerca de quatro semanas de janela útil, e o projeto pesa 100%
da avaliação.

O edital exige também declaração de vínculo com membros do corpo docente (Anexo II) — ou seja,
**é preciso conversar com um orientador antes**, o que reduz ainda mais a janela real.

---

## Bug encontrado no coletor

O PDF sem camada de texto extraía para `""`, e o hash era `sha256("")` — **idêntico para todo PDF
digitalizado**. Um edital substituído nunca seria detectado como mudança, e o silêncio seria
indistinguível de "nada mudou". Era a falha mais grave possível neste sistema, porque é silenciosa.

Corrigido em `backend/app/collector.py`: abaixo de `MIN_PDF_TEXT` (200 caracteres) o hash cai para os
bytes brutos e a `Fetched` marca `text_extractable=False`; o snapshot registra a base do hash em
`notes` e o monitor imprime `(bytes)`. O custo é aceito conscientemente — um re-scan idêntico pode
gerar alarme falso —, mas alarme falso se verifica em trinta segundos e cegueira não se verifica
nunca. Coberto por `tests/test_collector.py::TestPdfWithoutATextLayer`.

## O que ainda falta verificar

- Docentes e projetos reais da linha TOTI — a aderência a IA é hipótese, não fato.
- Grade horária concreta do PPGPEP: sabe-se que é noturno, mas os horários por disciplina ainda não
  foram transcritos como foram os do PPGCC.
- Frequência mínima exigida.
- Anexo II: quais docentes aceitam orientação neste ciclo.
