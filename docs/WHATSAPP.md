# WhatsApp: é possível, e o risco cai justamente no nosso caso

**Pergunta:** notificar no WhatsApp usando o próprio número, mandando mensagem para
si mesmo. Existe solução FOSS?

**Resposta curta:** existe, funciona, e o padrão de uso deste projeto é exatamente o
que a detecção do WhatsApp pontua como mais suspeito. Com o número que você usa na
FAI, eu não faria.

## O que existe, tecnicamente

Três caminhos, e só um é oficial:

| Caminho | Número próprio? | ToS | Estado |
| --- | --- | --- | --- |
| **WhatsApp Cloud API** (Meta) | ❌ exige número **dedicado** | ✅ permitido | oficial; um número registrado nela não volta para o app |
| **Baileys** (TS) / **whatsmeow** (Go) | ✅ liga como dispositivo | ❌ viola | bibliotecas FOSS maduras; falam o protocolo multi-dispositivo |
| **Evolution API** (FOSS, Node) | ✅ | ❌ viola | empacota Baileys/whatsmeow numa API REST; muito usada no Brasil, self-hosted |

Do lado técnico, o que você quer é trivial: com qualquer uma das três não-oficiais,
o número é ligado como um **dispositivo adicional** (o mesmo mecanismo do WhatsApp
Web) e mandar mensagem para o próprio JID funciona — o WhatsApp tem a conversa
"Mensagem para mim" nativamente.

Você não é o único com esse problema, e a Evolution API existe justamente porque
muita gente quis isso.

## Por que eu não recomendo, e não é por ToS abstrato

A violação de termos é real, mas o que decide é a evidência empírica de 2025–2026:

- O WhatsApp disparou avisos de **"sua conta pode estar em risco — ferramentas não
  autorizadas"** e **banimentos** para usuários de whatsmeow, e a mesma onda pegou
  Baileys.
- Os banimentos atingiram uso **legítimo, de baixo volume e só-resposta** — não
  apenas quem fazia disparo em massa.
- A detecção pondera fortemente três sinais: **razão de resposta** (abaixo de 10% =
  alto risco), distância no grafo de contatos, e regularidade temporal.

O primeiro sinal é o problema. **Um bot de notificação só envia e nunca recebe
resposta** — razão de resposta ≈ 0%. E mensagens disparadas por um timer às 08:00 e
20:00 são o padrão temporal mais robótico possível. Ou seja: o nosso caso de uso não
é um uso de baixo risco que por azar pode cair. É o perfil que o classificador
procura.

Somado a isso: **é o número que você usa na FAI.** O custo de um banimento não é
perder a notificação — é perder o número de trabalho. Assimetria péssima para
economizar um app no celular.

> **Decidido em 11/08/2026: só ntfy.** Sem e-mail, sem WhatsApp. O tópico está
> configurado no `.env` e as duas primeiras notificações foram entregues.

## O que eu faria, em ordem

**1. ntfy — feito.** Custa zero e não tem risco nenhum. O tópico é **gerado
aleatoriamente**, não escolhido: no ntfy.sh público o tópico É a credencial, então
"gradradar" ou "editais" seriam adivinhados em segundos. O JP e o César assinam o
mesmo tópico. O único custo real é um ícone a mais no celular.

```
NOTIFY_CHANNELS=ntfy
NTFY_URL=https://ntfy.sh
NTFY_TOPIC=<gerado; está no .env, que é gitignored>
```

**2. Se quiser WhatsApp mesmo: um chip dedicado.** Aí o caminho é a **Cloud API
oficial** — sem risco de banimento, porque é permitido. O custo é o número
dedicado, um WhatsApp Business Account e um template `utility` aprovado para
mensagem iniciada pelo sistema. Você mesmo levantou essa possibilidade meses atrás,
e continua sendo a saída certa.

**3. Evolution API no seu número, se você aceitar o risco.** Não vou fingir que não
funciona. Se for esse o caminho, o mínimo é: rodar self-hosted, mandar **só** para
si mesmo, volume baixíssimo, e aceitar que o número pode cair sem aviso. Não use o
número da FAI.

## O slot do adaptador

`app/notify.py` tem `SENDERS`, um dicionário de canal → função. Adicionar WhatsApp é
escrever um `_send_whatsapp` do lado dos outros; nada mais no sistema precisa saber.
A decisão aqui é de risco, não de arquitetura — e é por isso que ela mora num
documento e não num TODO no código.

## Fontes

- [Aviso "sua conta pode estar em risco" atingindo whatsmeow e Baileys](https://github.com/tulir/whatsmeow/issues/810)
- [O que é Baileys — guia 2026](https://whatsapp.checkleaked.cc/blog/what-is-baileys)
- [Por que bots baratos derrubam seu número](https://sporesec.com/en/blog/whatsapp-unofficial-api-ban-risk)
- [Evolution API — projeto FOSS](https://github.com/evolution-foundation/evolution-api)
