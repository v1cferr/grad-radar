# Aderência ao trabalho na FAI

"Uma pós mais alinhada com o que fazemos na FAI" precisa ser algo verificável, ou
a varredura da USP vira gosto pessoal. Este documento converte as atribuições do
[Edital FAI 001/2026](editais/README.md) em sinais que se procuram na página de um
programa.

**Isto é critério de PONTUAÇÃO, não eliminatório.** Um programa perfeitamente
aderente que não tenha aula à noite continua fora — ver [`GOAL.md`](GOAL.md). A
ordem importa: primeiro os quatro requisitos, depois esta régua.

## Os cinco sinais

Derivados um a um do item 4.1 do edital. A coluna de evidência é o que conta como
verificado — nome de linha de pesquisa **não** conta, porque nome de linha promete
mais do que entrega (foi assim que a AMPLN do PPGCC pareceu forte e a oferta
noturna derrubou tudo).

| # | Sinal | Vem de | Evidência que conta |
| --- | --- | --- | --- |
| 1 | **Adoção organizacional de IA** | 4.1b, 4.1f — "impacto de inserção de IA em organizações", "oportunidades para implantação em setores" | docente com publicação ou projeto sobre adoção/difusão de tecnologia em organizações; dissertação defendida no tema |
| 2 | **IA técnica aplicada** | 4.1a — "pesquisa e avaliação de ferramentas e tecnologias de IA" | disciplina de ML/PLN/LLM ofertada de fato no semestre; laboratório ativo |
| 3 | **Dados e processos** | 2.2, 4.1c — "sistematização de processos", "levantamento, organização e pré-processamento de dados" | linha de engenharia de dados, modelagem de processos, sistemas de informação |
| 4 | **Restrições e governança** | 4.1d — "analisar as restrições no uso de tecnologias de IA" | disciplina ou projeto sobre regulação, LGPD, ética ou risco de IA |
| 5 | **Capacitação** | 4.1e — "treinamento em conceitos relacionados à IA aos colaboradores" | pesquisa em formação, transferência de tecnologia ou extensão |

Um programa que atende 1 e 3 serve para pesquisar o trabalho. Um que atende 2
serve para fazer o trabalho. O ideal atende os dois, e é essa a busca.

O veredito aplicado, programa por programa, está em [`PROGRAMAS.md`](PROGRAMAS.md).

## A tensão que já existe

O único programa aprovado nos quatro requisitos, o **PPGPEP**, é forte no sinal 1
e fraco no 2. A linha **TOTI** — Trabalho, Organizações, Tecnologia e Inovação —
descreve quase literalmente o item 4.1b, e o trabalho na FAI seria o campo
empírico de uma dissertação dela.

Mas isso é aderência ao **escopo declarado** da linha, não a docentes e projetos
reais. É a diferença entre o sinal 1 estar plausível e estar verificado, e é
exatamente o erro que a régua acima tenta evitar. O levantamento está pendente.

Do outro lado, o **PPGCC** e o **PIPGEs** são fortes no sinal 2 — o PIPGEs tem
linha explícita de Aprendizado de Máquina — e ambos morreram no requisito de
horário. Isto não é coincidência: a oferta noturna é estrutural dos programas
**profissionais**, e a IA técnica se concentra nos **acadêmicos**. É a tensão
central do projeto, e é o motivo de valer varrer a USP.

## O que isto pede da USP

O ICMC é o candidato óbvio no sinal 2, e é onde o risco de repetir o PPGCC é
maior: programa acadêmico forte, provavelmente diurno. Então a ordem da varredura
é a mesma que já se provou aqui — **grade horária primeiro**. Só depois de saber
que existe aula depois das 18h vale investigar aderência, porque investigar
aderência de programa eliminado é o trabalho que já se fez três vezes.

Vale olhar além do ICMC pelos sinais 1, 3 e 5, que não são de computação:
engenharia de produção, administração, ciência da informação. O sinal 1 mora
nesses departamentos, não no de computação — foi lá que o PPGPEP apareceu.

## Por que não está no banco ainda

O modelo tem [`ProgramRequirement`](../backend/app/models/eligibility.py) para os
eliminatórios, com evidência por fato. Estes cinco sinais são a próxima tabela
natural, e ela não foi criada de propósito: com um programa aprovado e nenhum dado
da USP, um esquema de pontuação seria desenhado sobre um caso só. Ele entra junto
com a varredura da USP, quando houver o que comparar.
