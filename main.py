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
SUPPORT_USER = "@ey_u01"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

pro_users = {OWNER_ID: 9999999999}
user_langs = {} 
user_modes = {} 

# ግሩፕ መግባታቸውን ማረጋገጫ
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except: return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"))
    builder.add(types.InlineKeyboardButton(text="🇪🇹 አማርኛ", callback_data="lang_am"))
    await message.answer(f"Welcome {message.from_user.first_name}! Select Language 👇", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("lang_"))
async def process_lang(callback: types.CallbackQuery):
    user_langs[callback.from_user.id] = callback.data.split("_")[1]
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="❓ Ask Question"), types.KeyboardButton(text="🖼 Create Image"))
    builder.row(types.KeyboardButton(text="💎 Get PRO Version"), types.KeyboardButton(text="🆘 Help"))
    await callback.message.answer("Eyu AI Ready! Ask anything.", reply_markup=builder.as_markup(resize_keyboard=True))
    await callback.answer()

@dp.message(F.text.contains("PRO") | F.text.contains("Get PRO"))
async def pro_info(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ ደረሰኝ ለመላክ (Submit Receipt)", url=f"https://t.me/ey_u01"))
    msg = (
        "💎 **Eyu AI PRO (High Intelligence & Fast Mode)**\n\n"
        "🔵 Telebirr: `0991923021` (Eyu)\n"
        "🟢 M-Pesa: `0713038680` (Eyu)\n"
        "🏦 CBE: `1000631943482` (Ermias)\n\n"
        "ክፍያ ከፈጸሙ በኋላ ደረሰኙን ከታች ባለው በተን ይላኩ 👇"
    )
    await message.answer(msg, reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.message(F.text.contains("Help") | F.text.contains("Help"))
async def help_info(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Contact Support", url=f"https://t.me/ey_u01"))
    await message.answer("ማንኛውም እርዳታ ከፈለጉ ከታች ያለውን በተን ይጫኑ 👇", reply_markup=builder.as_markup())

@dp.message()
async def handle_all(message: types.Message):
    uid = message.from_user.id
    is_pro = uid in pro_users and time.time() < pro_users[uid]

    # 1. Group Check (ሁሉንም ያስገድዳል)
    if not await check_subscription(uid) and uid != OWNER_ID:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Join Group", url=GROUP_URL))
        return await message.answer(f"⚠️ ቦቱን ለመጠቀም መጀመሪያ ግሩፑን መቀላቀል አለብዎት፦\n{GROUP_URL}", reply_markup=builder.as_markup())

    if "Question" in message.text or "ጥያቄ" in message.text:
        user_modes[uid] = "chat"
        return await message.answer("ጥያቄዎን ይጻፉ...")
    elif "Image" in message.text or "ምስል" in message.text:
        user_modes[uid] = "image"
        return await message.answer("የምስሉን መግለጫ ይጻፉ...")

    mode = user_modes.get(uid, "chat")
    if mode == "image":
        async with ChatActionSender.upload_photo(chat_id=message.chat.id, bot=bot):
            url = f"https://image.pollinations.ai/prompt/{message.text}?model=flux&width=1024&height=1024&nologo=true"
            await message.answer_photo(URLInputFile(url), caption="By Eyu AI 😎")
    else:
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            # PRO ተጠቃሚ ፈጣን ሞዴል ያገኛል
            model = "search" if is_pro else "openai"
            url = f"https://text.pollinations.ai/{message.text}?model={model}&nologo=true"
            ans = requests.get(url).text.split("---")[0].strip()
            await message.answer(f"💡 AI ({'PRO' if is_pro else 'Free'}):\n\n{ans}")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
