> ## Telegram Bot - Sistema Automático de Vendas via Telegram
>
> Um bot de **vendas automáticas** para o Telegram integrado com **Pix e Mercado Pago**, desenvolvido em Python.
> Ele gerencia **produtos digitais**, **estoque**, **saldo de usuários**, **promoções automáticas** e **programa de parcerias**.
>
> 💡 **Principais recursos:**
>
> * Pagamentos automáticos via Pix (Mercado Pago API)
> * Sistema de saldo e depósito com QR Code
> * Estoque automático com leitura de `.txt`
> * Programa de parceiros com comissões
> * Área para revendedores e fornecedores
> * Banco de dados SQLite local
> * Integração de Webhook para confirmação automática
>
> ⚙️ **Tecnologias usadas:**
>
> * Python 3
> * Flask (para webhook)
> * python-telegram-bot v20+
> * mercadopago SDK
> * qrcode
> * SQLite3
>
> 🚀 **Como usar:**
> 1. Execute no terminal do vscode, ou no cmd dentro da pasta do bot `pip install -r requirements.txt`
> 2. Configure os tokens no arquivo `bot.py` e `webhook-server.py`
> 3. Crie o banco executando `init_db()` na primeira inicialização
> 4. Rode o bot com:
>
>    ```bash
>    python bot.py
>    ```
> 4. Rode o webhook com:
>
>    ```bash
>    python webhook-server.py
>    ```
>
> 📦 **Arquivos principais:**
>
> * `bot.py` → Lógica principal do bot
> * `webhook-server.py` → Confirmações automáticas do Pix
> * `products.json` → Lista de produtos disponíveis
>
> 

## 🛠️ Comandos de Administrador

> ⚙️ Estes comandos só podem ser usados por IDs que estão listados em:
>
> ```python
> ADMIN_IDS = ["123456789"]
> ```
>
> Substitua pelo seu ID real antes de iniciar o bot.

---

### 💰 Gerenciamento de Saldo

| Comando                       | Descrição                                | Exemplo                  |
| ----------------------------- | ---------------------------------------- | ------------------------ |
| `/addsaldo <user_id> <valor>` | Adiciona saldo manualmente a um usuário. | `/addsaldo 123456789 10` |
| `/remsaldo <user_id> <valor>` | Remove saldo manualmente de um usuário.  | `/remsaldo 123456789 5`  |

---

### 🏪 Gerenciamento de Produtos e Estoque

| Comando                                    | Descrição                                                    | Exemplo                                 |
| ------------------------------------------ | ------------------------------------------------------------ | --------------------------------------- |
| `/addstock <id_produto> <lista_de_contas>` | Adiciona contas manualmente a um produto.                    | `/addstock conta1 email:senha`          |
| `/remstock <id_produto> <email:senha>`     | Remove uma conta específica do estoque disponível.           | `/remstock conta1 email@teste.com:1234` |
| `/addfakestock <id_produto> <quantidade>`  | Adiciona unidades ao estoque **falso (visual)**.             | `/addfakestock conta1 10`               |
| `/remfakestock <id_produto> <quantidade>`  | Remove unidades do estoque **falso (visual)**.               | `/remfakestock conta1 5`                |
| `/setfakestock <id_produto> <quantidade>`  | Define um novo valor fixo para o estoque **falso (visual)**. | `/setfakestock conta1 15`               |
| `/stock`                                   | Mostra a quantidade atual de estoque real de cada produto.   | `/stock`                                |
| `/stock_detalhado <id_produto>`            | Mostra detalhes do estoque de um produto.                    | `/stock_detalhado conta1`               |

💡 **Dica:**
Você também pode enviar um **arquivo `.txt` com as contas**, e colocar o **ID do produto na legenda**.
O bot vai ler automaticamente e adicionar todas as contas válidas ao estoque.

---

### 👥 Programa de Parcerias (Afiliados)

| Comando                      | Descrição                                                  | Exemplo                   |
| ---------------------------- | ---------------------------------------------------------- | ------------------------- |
| `/addpartner <user_id>`      | Adiciona um usuário ao programa de parceiros.              | `/addpartner 123456789`   |
| `/rempartner <user_id>`      | Remove um usuário do programa de parceiros.                | `/rempartner 123456789`   |
| `/listpartners`              | Lista todos os parceiros, indicações e total de comissões. | `/listpartners`           |
| `/partnerstats <partner_id>` | Mostra estatísticas detalhadas de um parceiro.             | `/partnerstats 123456789` |

🪙 **O que é um parceiro:**
Um parceiro ganha **comissão automática** sempre que um usuário indicado fizer uma compra.
O valor da comissão é definido pela variável `TAXA_COMISSAO_PARCEIRO` no código.

---

### 🧑‍🏭 Gerenciamento de Fornecedores (Revendedores)

| Comando              | Descrição                                   | Exemplo              |
| -------------------- | ------------------------------------------- | -------------------- |
| `/addforn <user_id>` | Torna o usuário um fornecedor (revendedor). | `/addforn 123456789` |
| `/remforn <user_id>` | Remove o status de fornecedor do usuário.   | `/remforn 123456789` |

---

### 🎉 Sistema de Promoções (Bônus em Depósitos)

| Comando                  | Descrição                                 | Exemplo        |
| ------------------------ | ----------------------------------------- | -------------- |
| `/promoon <porcentagem>` | Ativa uma promoção de bônus em depósitos. | `/promoon 25`  |
| `/promooff`              | Desativa a promoção.                      | `/promooff`    |
| `/promostatus`           | Mostra o status atual da promoção.        | `/promostatus` |

💎 Exemplo:
Com `/promoon 25`, cada depósito ganha **+25% de bônus** no saldo do usuário.

---

### 🔐 Outros Comandos Úteis

| Comando        | Descrição                        | Exemplo   |
| -------------- | -------------------------------- | --------- |
| `/pix <valor>` | Gera um QR Code Pix manualmente. | `/pix 10` |
| `/stock`       | Mostra o status do estoque real. | `/stock`  |

---

### 🤖 Funções Automáticas do Bot

* 🚨 Aviso automático de **estoque baixo** (configurado em `LIMITE_ESTOQUE_BAIXO`)
* 💸 Processamento automático de **PIX via Webhook**
* 📈 Cálculo e envio de **comissões automáticas** para parceiros
* 🧾 Relatórios automáticos ao adicionar estoque
* 👤 Criação automática de usuários ao usar `/start`

---



> 
> 🧑‍💻 *Desenvolvido por João Vitor — estudante autodidata de pentest e automação.*
