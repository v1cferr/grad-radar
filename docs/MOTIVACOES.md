# Motivações

Por que o GradRadar existe, e por que ele é construído desta forma.

Este documento não descreve funcionalidades — isso é o [README](../README.md). Ele registra o raciocínio que
define os requisitos. Quase toda decisão de produto sai daqui: por que horário é filtro de primeira classe, por
que aluno especial ganha módulo próprio, por que existe o estado `aguardando edital`, por que a pontuação é por
candidato. Quando uma decisão de design parecer arbitrária mais adiante, é este arquivo que a explica.

Escrito em português por ser documento de contexto e decisão. O código, o README e a documentação técnica
seguem o princípio *English-first* declarado em [`GITHUB.md`](./GITHUB.md).

---

## O objetivo

Entrar numa pós-graduação **pública, gratuita e presencial** em Computação com foco em Inteligência
Artificial, no ecossistema de São Carlos — UFSCar e USP/ICMC.

O sistema é construído para **duas pessoas**: Victor e João Pedro (JP). Não é um catálogo genérico de cursos;
é um instrumento de decisão compartilhado entre dois candidatos que trabalham em período comercial e precisam
avaliar as mesmas oportunidades sob restrições diferentes.

O foco em IA não é preferência abstrata: é a área em que já trabalhamos hoje. A pós precisa somar com isso, não
correr em paralelo.

## O problema real

A informação existe, mas está espalhada entre páginas institucionais, editais em PDF, páginas de departamento,
sites de laboratório, Currículos Lattes, notícias e sistemas de inscrição. Cada fonte usa um formato diferente
e nenhuma responde a pergunta que importa.

Consequência prática: descobrir uma oportunidade excelente **tarde** é indistinguível de não descobrir. Um
edital que abriu e fechou enquanto ninguém olhou a página custa um semestre inteiro — ou um ano.

É por isso que este projeto é um *radar*, e não uma planilha. Planilha não avisa.

## Princípios de decisão

Quatro regras que o sistema precisa respeitar.

**1. Não cravar "pós necessariamente este ano".** Diploma primeiro; depois editais, linhas de pesquisa,
horários, docentes, talvez aluno especial. Se aparecer uma oportunidade excelente ainda em 2026, ótimo. Se a
melhor janela for 2027, a trajetória não muda. O sistema existe para me ajudar a **reconhecer** a melhor
janela, não para apressar a primeira que aparecer.

**2. Aluno especial é porta de entrada, não consolo.** Cursar disciplina isolada antes do ingresso formal é a
forma de baixo compromisso de testar o que nenhum edital informa: o nível real das aulas, o horário funcionando
na prática, o ambiente presencial, a afinidade com um possível orientador. E os créditos podem ser aproveitados
depois. É instrumento de decisão, e por isso é módulo, não rodapé.

**3. Sustentabilidade é critério de viabilidade, não de conforto.** Uma pós que só "cabe" no papel — porque a
disciplina é à noite e o resto se resolve — não cabe. Deslocamento até o campus, frequência obrigatória, carga
de trabalhos e a jornada de trabalho de oito horas entram na mesma conta. Um programa incompatível com a rotina
não é uma opção pior: é uma opção falsa.

**4. Dois candidatos, restrições diferentes.** Não existe "o melhor programa". A mesma oportunidade pode ser
prioridade máxima para um e inviável para o outro, por horário, deslocamento, linha de pesquisa ou documentação
pendente. Qualquer ranking global estaria errado para pelo menos um dos dois.

## Fontes oficiais e rastreabilidade

Agregadores de terceiros ficam desatualizados e erram datas. Só a página oficial e o PDF do edital valem como
fonte, e o sistema precisa preservar o original, registrar quando foi verificado pela última vez e detectar
quando mudou.

Editais são revisados: prazo prorrogado, vaga alterada, documento adicionado. Guardar apenas a versão mais
recente perde exatamente a informação que importa — **o que mudou**.

## Notificações

Alerta que não é visto não é alerta. O canal precisa ser aquele que nós dois já conferimos várias vezes por
dia — por isso o alvo é **WhatsApp**, não e-mail e não um painel que exige lembrar de abrir.

O sistema é desenhado com os canais habilitados por configuração, de modo que adicionar ou trocar canal seja
configuração e não código. Isso mantém a escolha do canal fora do caminho crítico do resto do projeto.

## Manual primeiro, automação depois

A coleta automatizada é a última fase de propósito. Enquanto o modelo de dados não estiver validado por uso
real, scraping só produziria dados errados mais rápido. Primeiro cadastrar à mão os dois programas que
importam, usar o fluxo, descobrir o que falta — depois automatizar o que já se provou útil.

---

## Implicações para o GradRadar

O que os princípios acima exigem do sistema, concretamente:

| Motivação | O que o sistema precisa fazer |
| --- | --- |
| Sustentabilidade é viabilidade | Horário não é metadado. Modelar **carga semanal real** — dia, horário, deslocamento até o campus, frequência obrigatória — e tratar compatibilidade com a jornada de trabalho como filtro de primeira classe, não observação em campo de texto. |
| Não cravar 2026 | `aguardando edital` é estado de pipeline de primeira classe. Rastrear o **próximo edital esperado**, não apenas o que está aberto — é isso que impede perder uma janela em 2027. |
| Descobrir tarde = não descobrir | Monitoramento com verificação periódica registrada, e alerta de prazo que dispara com antecedência suficiente para preparar documentos, não no dia do fechamento. |
| Aluno especial como porta de entrada | Módulo próprio, com horário, ementa, docente e possibilidade de aproveitamento de créditos — e ligado ao mesmo pipeline do ingresso regular. |
| Dois candidatos, restrições diferentes | Pesos de pontuação **por candidato**, e não um ranking global. Cada um com seus interesses, restrições de horário, checklist de documentos e histórico. |
| Fontes oficiais e rastreabilidade | Guardar o link oficial e o PDF, com `last_checked_at` e hash de conteúdo. Editais versionados, com diferença entre versões — prazo prorrogado é a informação, não ruído. |
| Diploma primeiro | O checklist precisa distinguir **pré-requisito bloqueante** de item desejável, e mostrar explicitamente o que impede elegibilidade agora. |
| Alerta que não é visto não é alerta | Notificação por WhatsApp para os dois candidatos, com canais habilitados por configuração para que trocar de canal não seja refatoração. |
| Manual primeiro | O modelo de dados precisa ser preenchível à mão sem atrito antes de existir qualquer coletor automático. |
| Foco em IA | Linhas de pesquisa não são texto livre: taxonomia própria (IA, ML, PLN, LLMs, RI, Ciência de Dados, Engenharia de Software, Visão, IHC) com pontuação de aderência por candidato. |
