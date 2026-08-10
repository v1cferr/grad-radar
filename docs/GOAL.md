# Objetivo

O que este sistema precisa entregar, em uma frase:

> **Avisar Victor, João Pedro e César, no WhatsApp, quando surgir uma oportunidade de pós-graduação que
> atenda a todos os requisitos eliminatórios — antes que o prazo feche.**

Tudo o mais é meio.

---

## Requisitos eliminatórios

Não são critérios de pontuação. Um programa que falhe em qualquer um deles não é uma opção pior; é uma
opção falsa, e o sistema deve tratá-lo como tal.

| # | Requisito | Por quê |
| --- | --- | --- |
| 1 | **Oferta noturna** — aula começando às 18h ou depois | Os três trabalham 08–18. Sem isso, não há como cursar. |
| 2 | **Presencial em São Carlos** (ou remoto real) | Mudar de cidade não está em questão. |
| 3 | **Gratuito** | Sem mensalidade. |
| 4 | **Público** | Universidade pública. |

O requisito 1 é o que elimina quase tudo, e foi descoberto só depois de olhar a grade horária de verdade —
não estava dito em lugar nenhum. Ver [`research/ufscar-oferta-noturna.md`](research/ufscar-oferta-noturna.md).

## Critérios de pontuação

Aplicam-se **apenas** ao que passou pelos eliminatórios:

- aderência ao trabalho na FAI — cinco sinais derivados do edital, em
  [`ADERENCIA.md`](ADERENCIA.md);
- docentes e laboratórios com atividade real na área — não o nome da linha;
- possibilidade de entrar antes como aluno especial;
- existência de bolsa compatível com vínculo empregatício;
- distância e deslocamento;
- potencial de rede e de impacto na carreira.

## Prioridade institucional

1. **UFSCar** — os três trabalham na FAI/UFSCar. Estudar onde se trabalha é o cenário preferido.
2. **USP São Carlos / ICMC** — mesma cidade, sem deslocamento adicional relevante.
3. **Outras** — só se 1 e 2 não oferecerem nada que passe pelos eliminatórios.

## Candidatos

| Nome | Jornada | Situação |
| --- | --- | --- |
| Victor | 08–18, FAI/UFSCar | trabalha com adoção institucional de IA e integração de LLMs |
| João Pedro | 08–18 | — |
| César | 08–18 | — |

Os três compartilham o mesmo bloqueio de horário, o que torna o requisito 1 comum a todos. Interesses e
pesos, porém, são **por candidato** — o modelo nunca assumiu um ranking global.

---

## Estado atual da busca

| Instituição | Programa | Eliminatórios | Situação |
| --- | --- | --- | --- |
| UFSCar | PPGCC | ❌ requisito 1 | eliminado — só 08–12 e 14–18 |
| UFSCar | PPGEE | ❌ requisito 1 | eliminado |
| UFSCar | PIPGEs | ❌ requisito 1 | eliminado — apesar de ter linha de Aprendizado de Máquina |
| UFSCar | **PPGPEP** (profissional) | ✅ **todos** | **INSCRIÇÕES ABERTAS: 20/08 a 14/09/2026** |
| UFSCar | PPGCTS, PPGCI, PPGEP | ❌ requisito 1 | eliminados com grade lida — e são os de MAIOR aderência (70%, 50%, 60%) |
| UFSCar | **PPGAdS** (profissional) | ⏳ edital permite noite | último candidato vivo além do PPGPEP e do MECAI |
| USP/ICMC | **MECAI** (profissional) | ⏳ edital permite **noturno** seg–qui | gratuito e presencial verificados; ciclo 002/2026 já fechou — monitorado |
| USP/ICMC | CCMC (acadêmico) | ⏳ horário não olhado | o programa técnico de referência em IA da região |

> **Edital PPGPEP 001/2026 — ingresso em 2027.** 25 vagas, sem distribuição por linha, sem bolsa.
> A seleção é 100% sobre um **projeto de pesquisa**: etapa 1 avalia o projeto escrito, etapa 2 é a
> defesa oral dele. Ou seja, o trabalho real acontece **antes** de 20/08.
> Ver [`research/ufscar-ppgpep-edital-001-2026.md`](research/ufscar-ppgpep-edital-001-2026.md).

O PPGPEP passa nos quatro, mas tem aderência fraca a IA técnica. O MECAI/ICMC é o oposto — forte no eixo
técnico, e com as aulas concentradas numa sexta que atravessa o horário comercial. O veredito programa por
programa, com nível de evidência, está em [`PROGRAMAS.md`](PROGRAMAS.md).

O padrão que a varredura de 47 programas expôs: **IA técnica mora nos programas acadêmicos; aula fora do
horário comercial mora nos profissionais.** Não é azar — é como os dois formatos são desenhados.

## O que falta o sistema fazer

1. **Monitorar** as fontes oficiais automaticamente e detectar edital novo ou alterado (F5) — o
   coletor funciona e cobre 13 fontes, mas ainda depende de `just monitor` rodado à mão; falta o
   timer systemd nos dotfiles.
2. **Avisar** os três no WhatsApp quando algo que passa nos eliminatórios aparecer (F4).

Sem essas duas, o sistema é um retrato — e o problema que ele existe para resolver é justamente que
descobrir tarde é indistinguível de não descobrir.
