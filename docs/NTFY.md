# Notificação por ntfy — como ligar e como testar

Canal escolhido em 11/08/2026: **só ntfy.** Sem e-mail, sem WhatsApp — o porquê do
WhatsApp está em [`WHATSAPP.md`](WHATSAPP.md).

## O que já está feito

Configurado e verificado: as duas primeiras notificações saíram com `ntfy 200`
(PPGPEP e PPGAdS, os dois processos abertos). O tópico está no `.env`, que é
gitignored.

## O que falta você fazer

**1. Instalar o app.** É FOSS:
[F-Droid](https://f-droid.org/packages/io.heckel.ntfy/) ou Play Store / App Store.

**2. Assinar o tópico.** O nome está no `.env`:

```bash
grep '^NTFY_TOPIC=' .env
```

No app: **+** → cole o nome do tópico → deixe o servidor como `ntfy.sh` → Assinar.

**3. Conferir.** O ntfy.sh guarda as mensagens recentes (~12h), então as duas já
enviadas devem aparecer assim que você assinar. Se não aparecerem:

```bash
just notify-dry   # mostra o que enviaria, sem enviar
just notify       # envia
```

**4. Ligar no timer.** A cadeia automática ainda não inclui o `notify` na unidade
ativa. Precisa de:

```bash
cd ~/Projects/GitHub/v1cferr/dotfiles
sudo nixos-rebuild switch --flake .#nixos-kingston
systemctl list-timers grad-radar-monitor
```

Depois disso roda sozinho às 08:00 e 20:00: coleta → reavalia horário → avisa.

**5. JP e César.** Instalam o app e assinam o mesmo tópico. Não há cadastro, conta
nem convite — assinar o tópico É o acesso.

## ⚠️ O tópico é a credencial

No servidor público `ntfy.sh` **não há autenticação**: quem souber o nome do tópico
pode **ler e publicar** nele. Por isso o nome foi **gerado aleatoriamente** em vez de
escolhido — `gradradar` ou `editais` seriam adivinhados em segundos, e aí qualquer
um poderia mandar um "PPGPEP: prazo prorrogado" falso.

Consequências práticas:

- não coloque o tópico em nada público (issue, print, commit);
- se ele vazar, gere outro e troque o `.env` — não há como revogar;
- se algum dia a notificação passar a conter algo que não seja edital público,
  o certo é auto-hospedar o ntfy com autenticação, não confiar na obscuridade do
  nome.

Hoje o conteúdo é prazo de edital público, então a obscuridade basta.

## O que você vai receber, e o que não vai

Seis eventos, e **nenhum deles é "conteúdo mudou"** — o raciocínio está em
[`AUTOMACAO.md`](AUTOMACAO.md). O resumo:

| Evento | Quando |
| --- | --- |
| processo aberto | apareceu edital que dá para fazer |
| **anúncio** | uma página vigiada ganhou linhas com cara de edital novo |
| prazo chegando | marcos de 30, 14, 7, 3 e 1 dia |
| edital mudou | retificação no PDF |
| fonte cegou | paramos de conseguir ler uma fonte |
| **veredito de horário mudou** | a grade passou a ter (ou perder) aula à noite |

Os dois em negrito são os que respondem "como vou saber quando sair edital novo" e
"como vou saber se o PPGCC abrir noturno".

**Próximos avisos esperados sem você fazer nada:** o lembrete de 30 dias do PPGPEP em
**15/08**, o de 7 dias em **07/09**, e o do PPGAdS conforme 09/10 se aproxima.

## Se um dia quiser trocar

`app/notify.py` tem `SENDERS`, um dicionário canal → função, e `REQUIRED_ENV`, que
diz quais variáveis cada canal exige. Telegram já está implementado e desligado;
basta `NOTIFY_CHANNELS=ntfy,telegram` com as credenciais. Nome desconhecido na lista
é ignorado, não derruba a cadeia.
