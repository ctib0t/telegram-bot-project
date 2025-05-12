import pandas as pd
import requests
from io import BytesIO
import difflib
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

EXCEL_URL = "https://raw.githubusercontent.com/ctib0t/telegram-student-bot/main/استفسارات1.xlsx"
BOT_TOKEN = ""

qa_dict = {}

# تحميل البيانات
async def load_data():
    global qa_dict
    if qa_dict:
        return qa_dict
    print("📥 تحميل الملف...")
    response = requests.get(EXCEL_URL)
    df = pd.read_excel(BytesIO(response.content))
    df = df.dropna(subset=['السؤال', 'الإجابة'])
    qa_dict = dict(zip(df['السؤال'], df['الإجابة']))
    print(f"✅ تم تحميل {len(qa_dict)} سؤال.")
    return qa_dict

# /start فقط لعرض لوحة الأسئلة
async def show_question_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await load_data()
    keyboard = [[q] for q in list(qa_dict.keys())]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("📋 اختر سؤالك من اللوحة أو اكتبه مباشرة:", reply_markup=reply_markup)

# عند أي رسالة
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await load_data()
    question_text = update.message.text.strip()

    # ✅ رسالة ترحيب عند أول رسالة من المستخدم في الجلسة
    if not context.user_data.get("welcomed"):
        await update.message.reply_text("👋 مرحباً بك في بوت الاستفسارات! اكتب سؤالك أو اختره من القائمة.")
        context.user_data["welcomed"] = True

    questions = list(qa_dict.keys())
    match = difflib.get_close_matches(question_text, questions, n=1, cutoff=0.3)

    if match:
        await update.message.reply_text(qa_dict[match[0]])
    else:
        await update.message.reply_text("❓ لم أستطع فهم سؤالك، حاول تكتبه بشكل أوضح أو استخدم القائمة.")

# إعداد البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", show_question_keyboard))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("✅ البوت يعمل، ويرحب بالمستخدم عند أول رسالة.")
app.run_polling()
