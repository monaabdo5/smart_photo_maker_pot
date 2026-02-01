import streamlit as st
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest

# --- 1. إعدادات الواجهة ---
st.set_page_config(page_title="Magic Photo Bot", page_icon="🎨")
st.title("🎨 بوت صانع الصور الكرتونية")

# --- 2. جلب الأسرار الآمنة ---
try:
    TOKEN = st.secrets["TELEGRAM_TOKEN"]
    BOT_NAME = st.secrets.get("TELEGRAM_BOT_NAME", "Smart Bot")
    st.success(f"✅ تم تفعيل الإعدادات لـ: {BOT_NAME}")
except Exception:
    st.error("❌ خطأ: لم يتم العثور على TELEGRAM_TOKEN في Secrets!")
    st.stop()

# --- 3. وظائف البوت الأساسية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"مرحباً! أنا {BOT_NAME} 🤖 أرسلي لي أي وصف وسأحوله لصورة كرتونية مذهلة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    context.user_data['prompt'] = user_prompt
    
    # أزرار اختيار الحجم
    keyboard = [
        [InlineKeyboardButton("مربع (1:1) 🟦", callback_data='1:1')],
        [InlineKeyboardButton("سينمائي (16:9) 🎞️", callback_data='16:9')],
        [InlineKeyboardButton("طولي (9:16) 📱", callback_data='9:16')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"وصف رائع: '{user_prompt}' ✨\nاختاري حجم الصورة الآن:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    prompt = context.user_data.get('prompt', 'Cartoon art')
    # إضافة لمسة كرتونية للوصف تلقائياً ✍️
    cartoon_prompt = f"{prompt}, cartoon style, 3d render, vibrant colors, high resolution"
    
    await query.edit_message_text("جاري الرسم... 🎨 يرجى الانتظار ثواني.")
    
    # تحديد الأبعاد بناءً على الاختيار
    w, h = 1024, 1024
    if query.data == '16:9': w, h = 1280, 720
    elif query.data == '9:16': w, h = 720, 1280

    image_url = f"https://pollinations.ai/p/{cartoon_prompt.replace(' ', '%20')}?width={w}&height={h}&seed=42"
    
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=image_url, caption="تفضلي صورتكِ الكرتونية! 🎈")

# --- 4. محرك التشغيل القوي (الحل لمشكلة الشبكة) ---
async def run_bot():
    # هنا "السر" التقني: إعداد طلبات اتصال تتحمل بطء الشبكة 📡
    request_config = HTTPXRequest(
        connection_pool_size=20, # فتح قنوات متعددة
        connect_timeout=60.0,    # الانتظار لمدة دقيقة للاتصال
        read_timeout=60.0        # الانتظار لدقيقة لقراءة البيانات
    )
    
    app = Application.builder().token(TOKEN).request(request_config).build()
    
    # ربط الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    st.info("📡 جاري محاولة فتح قناة الاتصال الآمنة مع تليجرام...")
    
    try:
        await app.initialize()
        await app.start_polling(drop_pending_updates=True)
        st.success("🚀 البوت يعمل الآن! اذهبي لتليجرام وجربيه.")
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        st.warning(f"🔄 محاولة إعادة اتصال تلقائية بسبب زحام الشبكة...")
        await asyncio.sleep(5)
        await run_bot() # إعادة المحاولة

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except Exception as e:
        st.error(f"⚠️ حدث خطأ غير متوقع: {e}")
