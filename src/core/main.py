import asyncio
from datetime import datetime
import pandas as pd
import requests
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton
from aiogram.enums import ParseMode
from aiogram import F
from database import db

config_data = db.get_config()
BOT_TOKEN = config_data['BOT_TOKEN']
OWNER_ID = config_data['OWNER_ID']
LOG_USER_ID = config_data['LOG_USER_ID']
TIMEZONE = config_data['TIMEZONE']

dynamic_data = db.get_dynamic_data()
COINMARKETCAP_API_KEYS = dynamic_data['COINMARKETCAP_API_KEYS']
USER_LIST = dynamic_data['USER_LIST']
ADMIN_LIST = dynamic_data['ADMIN_LIST']
BANNED_USERS = dynamic_data['BANNED_USERS']
FOOD_RESERVATION_LIST = dynamic_data['FOOD_RESERVATION_LIST']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

time_zone = pytz.timezone(TIMEZONE)
cmc_api_keys = COINMARKETCAP_API_KEYS
user_list = USER_LIST
admin_list = ADMIN_LIST
banned_users = BANNED_USERS
reminder_list = FOOD_RESERVATION_LIST

class UserStates(StatesGroup):
    waiting_for_message = State()
    admin_waiting_for_message = State()

def create_admin_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🆘 Help"))
    keyboard.add(KeyboardButton(text="👑 Admins"))
    keyboard.add(KeyboardButton(text="👥 Users"))
    keyboard.add(KeyboardButton(text="📩 Message"))
    keyboard.add(KeyboardButton(text="⏰ Reminder"))
    keyboard.add(KeyboardButton(text="💰 Coin"))
    keyboard.adjust(2, repeat=True) 
    return keyboard.as_markup(resize_keyboard=True)

def create_user_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🆘 Help"))
    keyboard.add(KeyboardButton(text="📩 Message"))
    keyboard.add(KeyboardButton(text="⏰ Reminder"))
    keyboard.add(KeyboardButton(text="💰 Coin"))
    keyboard.adjust(2, repeat=True) 
    return keyboard.as_markup(resize_keyboard=True)

def create_back_keyboard(is_admin: bool):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="🔙 Back to Main Menu"))
    return keyboard.as_markup(resize_keyboard=True)

async def log_message(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    if user_id == OWNER_ID:
        return
    
    if user_id not in user_list:
        user_list.append(user_id)
    
    await bot.forward_message(chat_id=LOG_USER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    log_message = f"🚀 New message from:\n👤 Name: {user_name}\n🆔 ID: {user_id}"
    await bot.send_message(chat_id=LOG_USER_ID, text=log_message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    if user_id in admin_list:
        await message.answer(f"Hello {user_name}:)\nWelcome to ChoLu 3.2! You are an admin. Press the Help button below for more information.", reply_markup=create_admin_keyboard())
    else:
        await message.answer(f"Hello {user_name}:)\nWelcome to ChoLu 3.2! Press the Help button below for more information.", reply_markup=create_user_keyboard())
    await log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "🆘 Help")
async def help_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in admin_list:
        help_message = (
            "Here's what you can do as an admin:\n\n"
            "👑 Admins:\n"
            "- View the list of admins.\n"
            "- Add or remove admins.\n\n"
            "👥 Users:\n"
            "- View the list of users.\n"
            "- Ban or unban users.\n\n"
            "💰 Coin:\n"
            "- Set your CoinMarketCap API Key.\n"
            "- View the latest prices of top cryptocurrencies.\n"
            "- View the list of registered APIs.\n\n"
            "⏰ Reminder:\n"
            "- Add yourself to the food reminder list.\n"
            "- Stop receiving food reminders.\n"
            "- View the list of users in the reminder list.\n"
            "- Add or remove users from the reminder list.\n\n"
            "📩 Message:\n"
            "- Send messages to users.\n\n"
            "If you need further assistance, contact the developer."
        )
    else:
        help_message = (
            "Here's what you can do:\n\n"
            "💰 Coin:\n"
            "- Set your CoinMarketCap API Key.\n"
            "- View the latest prices of top cryptocurrencies.\n\n"
            "⏰ Reminder:\n"
            "- Add yourself to the food reminder list.\n"
            "- Stop receiving food reminders.\n\n"
            "📩 Message:\n"
            "- Message the developer anonymously.\n\n"
            "If you need further assistance, contact the developer."
        )
    await message.answer(help_message)
    await log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "👑 Admins")
async def admins_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to access this command.")
        await log_message(message)
        return
    
    admins_info = []
    for admin_id in admin_list:
        try:
            user = await bot.get_chat(admin_id) 
            admins_info.append(f"👤 {user.full_name} (🆔 {admin_id})")
        except Exception as e:
            admins_info.append(f"👤 Unknown User (🆔 {admin_id})")
    
    admins_message = (
        f"👑 List of Admins:\n{'\n'.join(admins_info)}\n\n"
        "To add an admin, use:\n"
        "/admin_add [user_id]\n\n"
        "To remove an admin, use:\n"
        "/admin_remove [user_id]"
    )
    
    await message.answer(admins_message)
    await log_message(message)

@dp.message(Command("admin_add"))
async def add_admin_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        await message.answer("Only the owner can use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /admin_add [user_id]")
        await log_message(message)
        return
    
    if target_id not in admin_list:
        admin_list.append(target_id)
        await message.answer(f"User {target_id} added to admins.")
    else:
        await message.answer(f"User {target_id} is already an admin.")
    
    await log_message(message)

@dp.message(Command("admin_remove"))
async def remove_admin_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        await message.answer("Only the owner can use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /admin_remove [user_id]")
        await log_message(message)
        return
    
    if target_id == OWNER_ID:
        await message.answer("The owner cannot be removed from admins.")
    elif target_id in admin_list:
        admin_list.remove(target_id)
        await message.answer(f"User {target_id} removed from admins.")
    else:
        await message.answer(f"User {target_id} is not an admin.")
    
    await log_message(message)
    
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "👥 Users")
async def users_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to access this command.")
        await log_message(message)
        return
    
    users_info = []
    for user_id in user_list:
        try:
            user = await bot.get_chat(user_id)
            user_name = user.full_name
        except Exception as e:
            user_name = "Unknown User"
        
        if user_id in banned_users:
            users_info.append(f"👤 {user_name} (🆔 {user_id}) ❌")  
        else:
            users_info.append(f"👤 {user_name} (🆔 {user_id})")  
    
    users_message = (
        f"👥 List of Users:\n{'\n'.join(users_info)}\n\n"
        "To manually add a user, use:\n"
        "/user_manual_add [user_id]\n\n"
        "To ban a user, use:\n"
        "/user_ban [user_id]\n\n"
        "To unban a user, use:\n"
        "/user_unban [user_id]"
    )
    
    await message.answer(users_message)
    await log_message(message)

@dp.message(Command("user_manual_add"))
async def user_manual_add_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        await message.answer("You do not have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /user_manual_add [user_id]")
        await log_message(message)
        return
    
    if target_id not in user_list:
        user_list.append(target_id)
        await message.answer(f"User {target_id} added to the user list.")
    else:
        await message.answer(f"User {target_id} is already in the user list.")
    
    await log_message(message)

@dp.message(Command("user_ban"))
async def user_ban_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /user_ban [user_id]")
        await log_message(message)
        return
    
    if target_id not in banned_users:
        if target_id not in admin_list:
            banned_users.append(target_id)
            await message.answer(f"User {target_id} has been banned.")
        else:
            if user_id == OWNER_ID:
                banned_users.append(target_id)
                await message.answer(f"User {target_id} has been banned.")
            else:
                await message.answer("You cannot ban an admin.")
    else:
        await message.answer(f"User {target_id} is already banned.")
    
    await log_message(message)

@dp.message(Command("user_unban"))
async def user_unban_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])  
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /user_unban [user_id]")
        await log_message(message)
        return
    
    if target_id in banned_users:
        if target_id not in admin_list:
            banned_users.remove(target_id)
            await message.answer(f"User {target_id} has been unbanned.")
        else:
            if user_id == OWNER_ID:
                banned_users.append(target_id)
                await message.answer(f"User {target_id} has been unbanned.")
            else:
                await message.answer("You cannot unban an admin.")
    else:
        await message.answer(f"User {target_id} is not banned.")
    
    await log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "📩 Message")
async def message_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in admin_list:
        await message.answer(
            "To send a message to users, use the following command:\n"
            "/send_message [user_id]\n"
            "Or to send to all users:\n"
            "/send_message all",
            reply_markup=create_admin_keyboard()
        )
        await log_message(message)
        return
    
    await message.answer(
        "📨 Send your message.\n"
        "This message will be sent anonymously to the bot developer.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(UserStates.waiting_for_message)
    await log_message(message)

@dp.message(Command("send_message"))
async def admin_send_message_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You don't have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target = message.text.split(maxsplit=1)[1].strip()
        
        if target.lower() == "all":
            await state.update_data(target_users="all")
        else:
            try:
                target_id = int(target)
                await state.update_data(target_users=[target_id])
            except ValueError:
                await message.answer("User ID must be a number or use 'all'")
                await log_message(message)
                return
        
        await message.answer(
            "Please send your message now.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(UserStates.admin_waiting_for_message)
        
    except IndexError:
        await message.answer("Invalid format. Please use:\n/send_message [user_id]\nor\n/send_message all")
    await log_message(message)

@dp.message(UserStates.admin_waiting_for_message)
async def handle_admin_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You don't have permission to use this command.")
        await log_message(message)
        await state.clear()
        return
    
    data = await state.get_data()
    target_users = data.get("target_users", [])
    
    success_count = 0
    failed_count = 0
    Errormsg = 0
    if target_users == "all":
        for target_id in user_list:
            if target_id not in banned_users and target_id != user_id:
                try:
                    await bot.copy_message(
                        chat_id=target_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    success_count += 1
                except Exception as e:
                    Errormsg = e
                    failed_count += 1
    else:
        for target_id in target_users:
            if target_id not in banned_users and target_id != OWNER_ID:
                try:
                    await bot.copy_message(
                        chat_id=target_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    success_count += 1
                except Exception as e:
                    Errormsg = e
                    failed_count += 1
    
    if target_users == "all":
        report_msg = f"✅ Message successfully sent to {success_count} users."
        if failed_count > 0:
            report_msg += f"\n❌ Failed to send to {failed_count} users. Error: {Errormsg}"
    else:
        if success_count > 0:
            report_msg = "✅ Message sent successfully."
        else:
            report_msg = f"❌ Failed to send message. Error: {Errormsg}"
    
    await message.answer(
        report_msg,
        reply_markup=create_admin_keyboard()
    )
    
    await log_message(message)
    await state.clear()

@dp.message(UserStates.waiting_for_message)
async def handle_user_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        await state.clear()
        return
    
    try:
        log_msg = f"📨 New message received from user:\n🆔 ID: {user_id}"
        await bot.send_message(chat_id=OWNER_ID, text=log_msg)
        await bot.forward_message(chat_id=OWNER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        
        await message.answer(
            "✅ Your message was sent successfully.\n",
            reply_markup=create_user_keyboard()
        )
        
    except Exception as e:
        await message.answer(f"❌ Error sending message. Please try again. Error: {e}")
    
    await log_message(message)
    await state.clear()

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "⏰ Reminder")
async def reminder_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="➕ Add to Food Reminder"))
    keyboard.add(KeyboardButton(text="➖ Stop Food Reminder"))
    
    if user_id in admin_list:
        keyboard.add(KeyboardButton(text="📜 Reminder List"))
    
    keyboard.add(KeyboardButton(text="🔙 Back to Main Menu"))
    keyboard.adjust(2, repeat=True) 
    
    await message.answer("Food Reminder Menu:", reply_markup=keyboard.as_markup(resize_keyboard=True))
    await log_message(message)

@dp.message(F.text == "➕ Add to Food Reminder")
async def add_to_reminder_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in reminder_list:
        reminder_list.append(user_id)
        await message.answer("You have been added to the food reminder list.")
    else:
        await message.answer("You are already in the food reminder list.")
    
    await log_message(message)

@dp.message(F.text == "➖ Stop Food Reminder")
async def stop_reminder_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in reminder_list:
        reminder_list.remove(user_id)
        await message.answer("You have been removed from the food reminder list.")
    else:
        await message.answer("You are not in the food reminder list.")
    
    await log_message(message)

@dp.message(F.text == "📜 Reminder List")
async def show_reminder_list_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to access this command.")
        await log_message(message)
        return
    
    reminder_info = []
    for user_id in reminder_list:
        try:
            user = await bot.get_chat(user_id)
            reminder_info.append(f"👤 {user.full_name} (🆔 {user_id})")
        except Exception as e:
            reminder_info.append(f"👤 Unknown User (🆔 {user_id})")
    
    reminder_message = (
        "📜 Reminder List:\n" + "\n".join(reminder_info) + "\n\n"
        "To add a user to the reminder list, use:\n"
        "/add_to_reminder [user_id]\n\n"
        "To remove a user from the reminder list, use:\n"
        "/remove_from_reminder [user_id]"
    )
    
    await message.answer(reminder_message)
    await log_message(message)

@dp.message(Command("add_to_reminder"))
async def add_to_reminder_admin_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /add_to_reminder [user_id]")
        await log_message(message)
        return
    
    if target_id not in reminder_list:
        reminder_list.append(target_id)
        await message.answer(f"User {target_id} has been added to the reminder list.")
    else:
        await message.answer(f"User {target_id} is already in the reminder list.")
    
    await log_message(message)

@dp.message(Command("remove_from_reminder"))
async def remove_from_reminder_admin_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return

    if user_id not in admin_list:
        await message.answer("You do not have permission to use this command.")
        await log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])  
    except (IndexError, ValueError):
        await message.answer("Invalid format. Use: /remove_from_reminder [user_id]")
        await log_message(message)
        return
    
    if target_id in reminder_list:
        reminder_list.remove(target_id)
        await message.answer(f"User {target_id} has been removed from the reminder list.")
    else:
        await message.answer(f"User {target_id} is not in the reminder list.")
    
    await log_message(message)

async def send_reminders():
    while True:
        now = datetime.now(time_zone)
        if now.weekday() == 2 and 22 <= now.hour < 23:  
            for user_id in reminder_list:
                try:
                    await bot.send_message(user_id, "🍽 رزرو غذا فراموش نشه!")
                except Exception as e:
                    pass
            await asyncio.sleep(7 * 24 * 3600) 
        else:
            await asyncio.sleep(3600)
            
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

CRYPTOS = {"BTC": "₿", "ETH": "Ξ", "USDT": "💵", "XRP": "✕", "BNB": "ⓑ", "SOL": "◎", "USDC": "💲", "DOGE": "🐶", "ADA": "🅰", "TRX": "🅿", "LINK": "🔗", "TON": "⚡"}

@dp.message(F.text == "💰 Coin")
async def coin_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    keyboard = ReplyKeyboardBuilder()
    for crypto, emoji in CRYPTOS.items():
        keyboard.add(KeyboardButton(text=f"{emoji} {crypto}"))
    
    if user_id in admin_list:
        keyboard.add(KeyboardButton(text="🔑 APIs"))
    
    keyboard.add(KeyboardButton(text="🔙 Back to Main Menu"))
    keyboard.adjust(3, repeat=True) 
    
    await message.answer("Choose a cryptocurrency:", reply_markup=keyboard.as_markup(resize_keyboard=True))
    await log_message(message)

@dp.message(Command("set_api_key"))
async def set_api_key_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    try:
        api_key = message.text.split(maxsplit=1)[1] 
    except IndexError:
        await message.answer("Invalid format. Use: /set_api_key [api_key]")
        return
    cmc_api_keys[str(user_id)] = api_key
    await message.answer("Your API Key has been set successfully!")
    await log_message(message)
    
@dp.message(F.text.in_([f"{emoji} {crypto}" for crypto, emoji in CRYPTOS.items()]))
async def handle_crypto_selection(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    api_key = cmc_api_keys.get(str(user_id))
    if not api_key or api_key == "" or api_key == "nan" or pd.isna(api_key):
        await message.answer("You need to set your CoinMarketCap API Key first. /how_to_set_api_key")
        await log_message(message)
        return
    
    crypto = message.text.split()[1]  
    
    try:
        price = await fetch_crypto_price(api_key, crypto)
        await message.answer(f"The current price of {crypto} is ${price}.")
    except Exception as e:
        await message.answer(f"Failed to fetch price for {crypto}: {str(e)}")
    
    await log_message(message)

async def fetch_crypto_price(api_key: str, crypto: str):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    params = {
        "symbol": crypto,
        "convert": "USD"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["data"][crypto]["quote"]["USD"]["price"]
    else:
        raise Exception("Failed to fetch data from CoinMarketCap API")
    
@dp.message(Command("how_to_set_api_key"))
async def how_to_set_api_key_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    help_message = (
        "📝 How to Get and Set Your CoinMarketCap API Key:\n\n"
        "1. Go to [CoinMarketCap API](https://pro.coinmarketcap.com/signup) and sign up for a free account.\n"
        "2. After signing up, navigate to the 'API Keys' section in your account dashboard.\n"
        "3. Generate a new API Key (it’s free for basic usage).\n"
        "4. Copy your API Key.\n"
        "5. In the bot, use the following command to set your API Key:\n"
        "   /set_api_key [Your_API_Key]\n\n"
        "Example:\n"
        "/set_api_key 12345678-90ab-cdef-1234-567890abcdef\n\n"
        "Once set, you can use the coin features in the bot! 🚀"
    )
    
    await message.answer(help_message, parse_mode=ParseMode.MARKDOWN)
    await log_message(message)

@dp.message(F.text == "🔑 APIs")
async def show_apis_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("You do not have permission to access this command.")
        await log_message(message)
        return
    
    apis_info = []
    for user_id, api_key in cmc_api_keys.items():
        if pd.isna(api_key) or str(api_key).strip() == "":
            continue 
        try:
            user = await bot.get_chat(int(user_id))
            apis_info.append(f"👤 {user.full_name} (🆔 {user_id}): {api_key}")
        except Exception as e:
            apis_info.append(f"👤 Unknown User (🆔 {user_id}): {api_key}")
    
    apis_message = "📜 List of APIs:\n" + "\n".join(apis_info)
    await message.answer(apis_message)
    await log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@dp.message(F.text == "🔙 Back to Main Menu")
async def back_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    if user_id in admin_list:
        await message.answer("Returning to the main menu.", reply_markup=create_admin_keyboard())
    else:
        await message.answer("Returning to the main menu.", reply_markup=create_user_keyboard())
    await log_message(message)
    
@dp.message(Command("database"))
async def handle_database_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        await message.answer("❌ Only admins can access this command")
        await log_message(message)
        return
    
    success = await db.export_database(
        bot=bot,
        chat_id=message.from_user.id,
        user_list=user_list,
        admin_list=admin_list,
        banned_users=banned_users,
        reminder_list=reminder_list,
        cmc_api_keys=cmc_api_keys
    )
    if not success:
        await message.answer("❌ Failed to export database")
    
    await log_message(message)

@dp.message()
async def forward_all_messages(message: types.Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("You have been banned from the bot. Message the developer to unban.")
        return
    
    await log_message(message)

async def start_reminder_scheduler():
    asyncio.create_task(send_reminders())

async def main():
    await start_reminder_scheduler()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
