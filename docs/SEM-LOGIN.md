# Por que não há login

Decisão: **o GradRadar não tem autenticação, e não é uma pendência.** A página é
aberta de qualquer lugar. Este documento existe para que a decisão não seja
refeita por reflexo, e para registrar a única condição que a reverteria.

## O que a página realmente mostra

Editais públicos e a nossa leitura deles. Datas, vagas, requisitos, linhas de
pesquisa, o que o edital cobra. **Nenhum nome de candidato é renderizado** — isso
foi verificado no HTML servido, não presumido: as buscas por "Victor", "João
Pedro" e "César" no HTML da página retornam zero. A única menção pessoal é a
palavra "FAI", numa frase sobre bolsa.

Uma senha protegeria informação que a UFSCar publica no próprio site.

## O argumento decisivo: o login mata o preview do link

O canal de entrega deste projeto é uma mensagem de WhatsApp com a URL. Todo o
valor está em o JP e o César verem, no preview, que existe prazo — sem abrir nada.

Um crawler de preview não faz login. Ele faz um GET e lê as tags OG do que
recebeu. Atrás de autenticação, o que ele recebe é a **tela de senha**, e o
preview passa a anunciar a tela de senha — ou nada. O trabalho descrito em
[`METADADOS.md`](METADADOS.md) deixaria de existir na prática.

Isto não é contornável com "libera o crawler": identificar crawler por
User-Agent é uma allowlist que qualquer um forja, e o resultado seria uma página
autenticada com um buraco público — pior que a página aberta, porque parece
protegida.

## O custo que não se paga

Autenticação não é uma tela. É tabela de contas, hash de senha, sessão, expiração,
recuperação de acesso, e um convite para o César que hoje é só um link. É
superfície de manutenção permanente para proteger o calendário de um processo
seletivo público.

E há o custo diário: três pessoas digitando senha para conferir uma data.

## O gatilho que reverteria isto

Uma linha, e ela é clara:

> **No momento em que a página passar a mostrar algo sobre uma PESSOA em vez de
> sobre um PROGRAMA, ela deixa de poder ser aberta.**

Exemplos concretos do que cruza a linha:

- anotação pessoal sobre um programa ou um orientador;
- ranking de preferência por candidato;
- rascunho de projeto de pesquisa;
- registro de conversa com docente, e-mail ou telefone de alguém;
- status de candidatura ("inscrito", "reprovado na etapa 1").

O último é o mais perigoso porque parece dado de sistema, e é o que mais dói
vazar.

**O que NÃO cruza a linha:** o `?candidate=` que já existe. Ele serve para
calcular conflito de horário contra a jornada 08–18 — que está publicada em
[`GOAL.md`](GOAL.md) e é a mesma para os três. Saber que existe alguém chamado
Victor com jornada comercial não é informação.

O aviso está plantado no código, em `frontend/web/src/app/page.tsx`, na linha do
`CANDIDATE` — que é por onde qualquer personalização vai entrar.

## O que fazer quando o gatilho for acionado

Não voltar ao `basic_auth` do Caddy. Ele já foi tirado
(`dotfiles/system/services/caddy.nix`), e voltar significaria duas senhas: a do
proxy e a do app. O caminho é login na aplicação, com duas consequências a aceitar
de propósito:

1. **Uma rota pública separada para o preview.** A página com dado pessoal fica
   atrás do login; o preview do link aponta para uma rota que só mostra prazo de
   edital público. É trabalho, e é o preço de ter as duas coisas.
2. **`noindex` continua.** Ele não tem relação com login e a razão dele não muda
   — ver [`METADADOS.md`](METADADOS.md).

## O que protege a página hoje

Não é segredo, e não se pretende que seja:

- **`noindex, nofollow` + `robots.txt`** — não aparece em busca, então não é
  encontrada por acaso;
- **URL não óbvia** — `pos.v1cferr.dev` não é adivinhada, mas isto é conveniência
  e não controle: qualquer um com o link entra, e é assim que deve ser;
- **fail2ban no SSH e o firewall do host** — protegem a máquina, não a página.

Se algum dia a página precisar de sigilo real, o item acima é a lista do que
**não** serve.
