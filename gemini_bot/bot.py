from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, InlineQueryHandler
import google.generativeai as genai
import uuid
from bot_config import bot_token, gemini_api_key

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("models/gemini-2.0-flash")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    bot_username = context.bot.username
    

    if update.message.chat.type == "private":
        user_msg = message_text
    elif f"@{bot_username}" in message_text:
        user_msg = message_text.replace(f"@{bot_username}", "").strip()
    else:
        return

    try:
        response = model.generate_content(user_msg)
        if response and response.candidates:
            text = response.candidates[0].content.parts[0].text
        else:
            text = "⚠️ No response from Gemini."
    except Exception as e:
        print(f"[ERROR] {e}")
        text = "❌ Gemini Error, please try again later."

    await update.message.reply_text(text)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return


    try:
        response = model.generate_content(query)
        if response and response.candidates:
            full_text = response.candidates[0].content.parts[0].text
        else:
            full_text = "⚠️ Gemini did not return any answer."
    except Exception as e:
        print(f"[ERROR] {e}")
        full_text = "❌ Gemini Error, please try again later."

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Send Gemini answer",
            input_message_content=InputTextMessageContent(full_text),
            description=query[:30]
        )
    ]
    await update.inline_query.answer(results, cache_time=0, is_personal=True)



app = ApplicationBuilder().token(bot_token).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(InlineQueryHandler(inline_query))

print("🤖 Gemini Telegram Bot is running...")
app.run_polling()
