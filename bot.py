from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters 
import json
import os

ARQUIVO_GASTOS = "gastos.json"

def carregar_gastos():
    if os.path.exists(ARQUIVO_GASTOS):
        with open(ARQUIVO_GASTOS, "r") as f:
            return json.load(f)
        return {}


def salvar_gastos(gastos):
    with open (ARQUIVO_GASTOS, "w") as f:
        json.dump(gastos, f)


def adicionar_gasto(usuario_id, valor):
    gastos = carregar_gastos()
    usuario_id = str(usuario_id)
    if usuario_id not in gastos:
        gastos[usuario_id] = []
    gastos[usuario_id].append(valor)
    salvar_gastos(gastos)

def total_gastos(usuario_id):
    gastos = carregar_gastos()
    usuario_id = str(usuario_id)
    if usuario_id in gastos:
        return sum(gastos[usuario_id])
    return 0


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update, context):
    teclado = [
        ["/total", "/listar"],   # primeira linha de botões
        ["/zerar", "/ajuda"]     # segunda linha de botões
    ]
    reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

    await update.message.reply_text(
        "Olá! 👋 Eu sou seu assistente financeiro.\n\n"
        "Você pode registrar um gasto enviando o valor (ex: 12,50).\n\nPara mais informações, utilize a opção /ajuda",
        reply_markup=reply_markup
    )


async def listar(update, context):
    usuario_id = str(update.message.from_user.id)
    gastos = carregar_gastos()

    if usuario_id not in gastos or len(gastos[usuario_id]) == 0:
        await update.message.reply_text("Você ainda não registrou nenhum gasto.")
        return 
    
    lista_formatada = "\n".join(
        [f"{i+1}. R${valor:.2f}" for i, valor in enumerate(gastos[usuario_id])]
    )

    total = sum(gastos[usuario_id])

    await update.message.reply_text(
        f"📋 Seus gastos:\n\n{lista_formatada}\n\n💰 Total: R${total:.2f}"
    )


async def total(update, context):
    usuario_id = update.message.from_user.id
    total_g = total_gastos(usuario_id)

    if total_g > 0:
        await update.message.reply_text(f"Seu total de gastos é R${total_g:.2f}.")
    else:
        await update.message.reply_text("Não há registro de gastos.")

async def zerar(update, context):
    usuario_id = str(update.message.from_user.id)
    gastos = carregar_gastos()

    if usuario_id in gastos:
        gastos[usuario_id] = []
        salvar_gastos(gastos)
        await update.message.reply_text("Seus gastos foram zerados. ✅")
    else:
        await update.message.reply_text("Você não possui gastos registrados.")


async def ajuda(update, context):
    await update.message.reply_text("Para adicionar um gasto, apenas envie o valor em formato numérico (ex: 12,50).\n\nCaso queira visualizar seus gastos totais, envie /total.\n\nGostaria de limpar o histórico de gastos? envie /zerar.")


async def echo(update, context):
    msg = update.message.text
    usuario_id = update.message.from_user.id

    try:
        # tenta converter a mensagem em número
        msg = msg.replace(",", ".")
        valor = float(msg)

        adicionar_gasto(usuario_id, valor)
        await update.message.reply_text(f"Gasto de R${valor:.2f} registrado!")

    except ValueError:
        # se não for número, verifica se é comando /total
        if msg.lower() == "/total":
            total = total_gastos(usuario_id)
            await update.message.reply_text(f"Seu total de gastos é R${total:.2f}")
        else:
            await update.message.reply_text("Envie um número para registrar gasto ou /total para ver o total.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("zerar", zerar))
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("O bot está rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()