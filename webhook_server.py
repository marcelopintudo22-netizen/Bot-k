# webhook_server.py
import sqlite3
import logging
import asyncio
import threading
import mercadopago
from flask import Flask, request, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# --- CONFIG ---
TOKEN = "TOKEN_DO_SEU_BOT_AQUI"
DB_FILE = "orders.db" # Bando de dados local
MERCADO_PAGO_TOKEN = "TOKEN_DO_MERCADO_PAGO_AQUI"
# --- FIM CONFIG ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=TOKEN)
sdk = mercadopago.SDK(MERCADO_PAGO_TOKEN)

def run_async_task(task):
    """Roda uma tarefa assíncrona de forma segura em um thread separado."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(task)

@app.route('/webhook/mercado-pago', methods=['POST'])
def mercado_pago_webhook():
    data = request.json
    if not (data and data.get("type") == "payment"):
        return jsonify(status="ignored, not a payment notification"), 200

    payment_id = data["data"]["id"]
    logger.info(f"Webhook recebido para o pagamento ID: {payment_id}")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM deposits WHERE payment_id = ? AND status = 'pending' AND cancelled = 0", (payment_id,))
    deposit = c.fetchone()

    if not deposit:
        logger.warning(f"Depósito com payment_id {payment_id} não encontrado ou já processado.")
        conn.close()
        return jsonify(status="deposit not found"), 200

    try:
        payment_info = sdk.payment().get(payment_id)
        if payment_info["status"] != 200:
            logger.error(f"Não foi possível obter informações do pagamento {payment_id}.")
            conn.close()
            return jsonify(status="error fetching payment"), 500

        payment = payment_info["response"]
        status = payment['status']

        if status == 'approved':
            original_amount = deposit['amount']
            total_amount_to_add = original_amount
            bonus_amount = 0
            
            c.execute("SELECT is_active, multiplier_percent FROM promotion WHERE id = 1")
            promo_data = c.fetchone()
            
            if promo_data and promo_data['is_active'] == 1:
                multiplier = promo_data['multiplier_percent'] / 100.0
                bonus_amount = original_amount * multiplier
                total_amount_to_add = original_amount + bonus_amount

            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (total_amount_to_add, deposit['user_id']))
            c.execute("UPDATE deposits SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE id = ?", (deposit['id'],))
            conn.commit()
            
            c.execute("SELECT balance FROM users WHERE user_id = ?", (deposit['user_id'],))
            new_balance_row = c.fetchone()
            new_balance = new_balance_row['balance'] if new_balance_row else 0
            
            async def notify_and_clean_up():
                success_text = f"✅ Pagamento de `R$ {original_amount:.2f}` confirmado com sucesso!"
                if bonus_amount > 0:
                    success_text = (f"✅ Pagamento de `R$ {original_amount:.2f}` confirmado!\n"
                                    f"🎉 Você ganhou um bônus de `R$ {bonus_amount:.2f}`!\n"
                                    f"💰 Total creditado: `R$ {total_amount_to_add:.2f}`")
                
                # ATUALIZAÇÃO: Edita a mensagem original do QR Code, espera, apaga e envia o menu.
                try:
                    await bot.edit_message_caption(chat_id=deposit['user_id'], message_id=deposit['message_id'], caption=success_text, parse_mode="Markdown", reply_markup=None)
                except Exception as e: # Se a mensagem não puder ser editada, envia uma nova
                    logger.warning(f"Não foi possível editar a mensagem {deposit['message_id']}: {e}. Enviando nova mensagem.")
                    await bot.send_message(chat_id=deposit['user_id'], text=success_text, parse_mode="Markdown")

                await asyncio.sleep(3)
                try:
                    await bot.delete_message(chat_id=deposit['user_id'], message_id=deposit['message_id'])
                except Exception as e:
                    logger.warning(f"Não foi possível apagar a mensagem {deposit['message_id']}: {e}")

                promo_banner = ""
                if promo_data and promo_data['is_active'] == 1:
                    bonus = int(promo_data['multiplier_percent'])
                    promo_banner = f"🎉 *PROMOÇÃO ATIVA!* 🎉\nDeposite e ganhe *{bonus}% de bônus* em saldo!\n\n"
                
                menu_text = (f"{promo_banner}"
                             "*🛒 | Bem vindo(a) a (Nome do seu bot aqui)💳* \n🌐 By - (Nome do seu bot aqui)\n\n"
                             "✅ (Informações de apresentação do seu bot aqui) \n"
                             "✅ (Informações de apresentação do seu bot aqui) \n"
                             "✅ (Informações de apresentação do seu bot aqui) \n\n"
                             "🔑 *Termos Importantes:*\n"
                             "┣ 🚫 Use sempre 4G.\n"
                             "┣ ⌛ Trocas: 10 minutos, com print.\n"
                             "┗ ⚠️ Não damos garantia de aprovação do seu pedido.\n\n"
                             "👤 *Seu perfil:*\n"
                             f"┣ 🆔 ID: `{deposit['user_id']}`\n"
                             f"┗ 💰 Saldo: `R$ {new_balance:.2f}`")
                menu_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔑 Produtos aqui", callback_data="menu_categories"), InlineKeyboardButton("💰 Adicionar Saldo", callback_data="deposit_start")],
                    [InlineKeyboardButton("🛒 Minhas Compras", callback_data="menu_my_accounts")],
                    [InlineKeyboardButton("🛍️ Para Revendedores", callback_data="menu_suppliers_categories")],
                    [InlineKeyboardButton("📜 Termos", callback_data="show_terms")],
                    [InlineKeyboardButton("💬 Grupo", url="LINK_DO_SEU_GRUPO_AQUI"), InlineKeyboardButton("💡 Suporte", url="LINK_DO_SEU_SUPORTE_AQUI")]
                ])
                await bot.send_message(chat_id=deposit['user_id'], text=menu_text, reply_markup=menu_keyboard, parse_mode="Markdown")
            
            thread = threading.Thread(target=run_async_task, args=(notify_and_clean_up(),))
            thread.start()
            logger.info(f"Saldo de {total_amount_to_add:.2f} adicionado para {deposit['user_id']}.")

        elif status in ['rejected', 'cancelled']:
            logger.warning(f"Pagamento {payment_id} para usuário {deposit['user_id']} com status '{status}'. Notificando usuário.")
            async def notify_failure():
                message_to_user = ""
                if status == 'cancelled':
                    message_to_user = "❌ **Pagamento Cancelado!**\n\nSua solicitação de depósito PIX foi cancelada."
                elif status == 'rejected':
                    message_to_user = "❌ **Pagamento Recusado!**\n\nSeu pagamento foi recusado pela instituição financeira."
                if message_to_user:
                    try:
                        await bot.edit_message_caption(chat_id=deposit['user_id'], message_id=deposit['message_id'], caption=message_to_user, parse_mode="Markdown", reply_markup=None)
                    except Exception: # Se a mensagem já foi apagada ou deu erro, apenas ignora
                        pass
            thread = threading.Thread(target=run_async_task, args=(notify_failure(),))
            thread.start()
        else:
            logger.info(f"Pagamento {payment_id} com status intermediário: '{status}'. Aguardando atualização final.")
    except Exception as e:
        logger.error(f"Erro CRÍTICO ao processar webhook para payment_id {payment_id}: {e}")
    finally:
        conn.close()
    return jsonify(success=True), 200

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
