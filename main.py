import asyncio
import time
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import URLInputFile
from aiogram.utils.chat_action import ChatActionSender

# --- መረጃዎች ---
API_TOKEN = '8363996272:AAG3auWiyGWtYMGI3Kcji3_u90V9N2S3z_g'
OWNER_ID = 8277735859 
GROUP_ID = "@ArtificialIntelligenceethio" 
GROUP_URL = "https://t.me/ArtificialIntelligenceethio"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

pro_users = {OWNER_ID: 9999999999} #
user_langs = {} 
user_modes = {} 

# --- AI Function (GPT-4o & Gemini 3.0 Integration) ---
async def get_ai_response(prompt, is_pro=False, lang="en"):
    if any(q in prompt.lower() for q in ["your name", "ስምህ", "ማነህ"]):
        return "እኔ የኢዩ (Eyu) AI ነኝ።" if lang == "am" else "I am Eyu AI."

    # PRO ለሆኑ Gemini 3.0 (Search) ፣ ለሌሎች GPT-4o (OpenAI)
    model = "search" if is_pro else "openai"
    url = f"https://text.pollinations.ai/{prompt}?model={model}&nologo=true"
    
    try:
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            # ማስታወቂያውን ለማጥፋት
            return r.text.split("---")[0].split("**Support")[0].strip()
        return "⚠️ Error: Connection issue."
    except: return "⚠️ Error: Timeout."

# --- Keyboard Generators ---
def main_menu(lang="en", is_pro=False):
    builder = ReplyKeyboardBuilder()
    q_txt = "❓ ጥያቄ ለመጠየቅ" if lang == "am" else "❓ Ask Question"
    i_txt = "🖼 ምስል ለመስራት" if lang == "am" else "🖼 Create Image"
    builder.row(types.KeyboardButton(text=q_txt), types.KeyboardButton(text=i_txt))
    if not is_pro:
        builder.row(types.KeyboardButton(text="💎 Get PRO Version"))
    
    # ✅ Help በተን ወደ @ey_u01 እንዲመራ
    builder.row(types.KeyboardButton(text="🆘 Help (@ey_u01)"))
    return builder.as_markup(resize_keyboard=True)

# --- Handlers ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"))
    builder.add(types.InlineKeyboardButton(text="🇪🇹 አማርኛ", callback_data="lang_am"))
    await message.answer(f"Welcome {message.from_user.first_name}! Select Language 👇", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("lang_"))
async def process_lang(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_langs[callback.from_user.id] = lang
    is_pro = callback.from_user.id in pro_users
    msg = "Eyu AI (GPT-4o & Gemini 3.0) Ready!"
    await callback.message.answer(msg, reply_markup=main_menu(lang, is_pro))
    await callback.answer()

# ✅ Help እና PRO ማስተካከያ
@dp.message(F.text.contains("Help") | F.text.contains("🆘"))
async def help_handler(message: types.Message):
    await message.answer("🆘 ለእርዳታ ወይም ለክፍያ @ey_u01 ን ያነጋግሩ።")

@dp.message(F.text.contains("PRO") | F.text.contains("💎"))
async def pro_request(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telebirr", callback_data="pay_tele"))
    builder.row(types.InlineKeyboardButton(text="🟢 M-Pesa", callback_data="pay_mpesa"))
    builder.row(types.InlineKeyboardButton(text="🏦 CBE", callback_data="pay_cbe"))
    builder.row(types.InlineKeyboardButton(text="✅ ደረሰኝ ላክ (Submit Receipt)", url="https://t.me/ey_u01"))
    txt = "💎 **PRO Version**\n1 Mo: 10 ETB | 6 Mo: 50 ETB"
    await message.answer(txt, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("pay_"))
async def pay_info(callback: types.CallbackQuery):
    method = callback.data.split("_")[1]
    info = {"tele": "0991923021", "mpesa": "0713038680", "cbe": "1000631943482"}
    await callback.message.answer(f"📍 {method.upper()}: `{info.get(method)}` \n👤 Name: Ermias Tura")
    await callback.answer()

@dp.message(Command("p"))
async def add_pro(message: types.Message):
    if message.from_user.id != OWNER_ID: return
    try:
        clean_text = message.text.replace("[", "").replace("]", "")
        args = clean_text.split()
        tid, days = int(args[1]), int(args[2])
        pro_users[tid] = time.time() + (days * 86400)
        await message.answer(f"✅ User {tid} PRO for {days} days.")
    except: pass

@dp.message()
async def handle_all(message: types.Message):
    uid = message.from_user.id
    lang = user_langs.get(uid, "en")
    is_pro = uid in pro_users and time.time() < pro_users[uid]

    if "ጥያቄ" in message.text or "Ask" in message.text:
        user_modes[uid] = "chat"
        await message.answer("ጥያቄዎን ይጻፉ...")
        return
    elif "ምስል" in message.text or "Image" in message.text:
        user_modes[uid] = "image"
        await message.answer("የምስሉን መግለጫ ይጻፉ...")
        return

    mode = user_modes.get(uid, "chat")
    if mode == "image":
        async with ChatActionSender.upload_photo(chat_id=message.chat.id, bot=bot):
            url = f"https://image.pollinations.ai/prompt/{message.text}?model=flux&width=1024&height=1024&nologo=true"
            await message.answer_photo(URLInputFile(url), caption="By Eyu AI 😎")
    else:
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            ans = await get_ai_response(message.text, is_pro, lang)
            await message.answer(f"💡 AI:\n\n{ans}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
