import threading
import time
from datetime import datetime, timedelta
import pandas as pd
import requests
import pytz
from databasecm import db
import telebot
from telebot import types

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

time_zone = pytz.timezone(TIMEZONE)
cmc_api_keys = COINMARKETCAP_API_KEYS
user_list = USER_LIST
admin_list = ADMIN_LIST
banned_users = BANNED_USERS
reminder_list = FOOD_RESERVATION_LIST

bot = telebot.TeleBot(BOT_TOKEN)

def log_message(message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    if user_id == OWNER_ID:
        return
    
    if user_id not in user_list:
        user_list.append(user_id)
    
    try:
        bot.forward_message(chat_id=LOG_USER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        
        log_text = (
            f"🚀 New message from: ( 🆔 {user_id} )\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.send_message(LOG_USER_ID, log_text)
        
    except Exception as e:
        print(f"Error logging message: {e}")

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    markup = types.ReplyKeyboardRemove(selective=False)
    
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    welcome_msg = f"Hello {user_name}:)\nWelcome to ChoLu 3.2!"
    if user_id in admin_list:
        welcome_msg += " You are an admin. Enter /help for more information."
    else:
        welcome_msg += " Enter /help for more information."
    
    bot.send_message(user_id, welcome_msg, reply_markup=markup)
    
    log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in admin_list:
        help_message = (
            "Here's what you can do as an admin:\n\n"
            "👑 /admins:\n"
            "- View the list of admins.\n"
            "- Add or remove admins.\n\n"
            "👥 /users:\n"
            "- View the list of users.\n"
            "- Ban or unban users.\n\n"
            "💰 /coin:\n"
            "- Set your CoinMarketCap API Key.\n"
            "- View the latest prices of top cryptocurrencies.\n"
            "- View the list of registered APIs.\n\n"
            "⏰ /reminder:\n"
            "- Add yourself to the food reminder list.\n"
            "- Stop receiving food reminders.\n"
            "- View the list of users in the reminder list.\n"
            "- Add or remove users from the reminder list.\n\n"
            "📩 /message:\n"
            "- Send messages to users.\n\n"
            "If you need further assistance, contact the developer."
        )
    else:
        help_message = (
            "Here's what you can do:\n\n"
            "💰 /coin:\n"
            "- Set your CoinMarketCap API Key.\n"
            "- View the latest prices of top cryptocurrencies.\n\n"
            "⏰ /reminder:\n"
            "- Add yourself to the food reminder list.\n"
            "- Stop receiving food reminders.\n\n"
            "📩 /message:\n"
            "- Message the developer anonymously.\n\n"
            "If you need further assistance, contact the developer."
        )
        
    bot.send_message(user_id, help_message)
    log_message(message)
    
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['admins'])
def admins_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to access this command.")
        log_message(message)
        return
    
    admins_info = []
    for admin_id in admin_list:
        try:
            user = bot.get_chat(admin_id)
            admins_info.append(f"👤 {user.first_name} (🆔 {admin_id})")
        except Exception as e:
            admins_info.append(f"👤 ID: {admin_id} (Unable to fetch name: {e})")
    
    admins_message = (
        f"👑 List of Admins:\n{'\n'.join(admins_info)}\n\n"
        "To add an admin, use:\n"
        "/admin_add [user_id]\n\n"
        "To remove an admin, use:\n"
        "/admin_remove [user_id]"
    )
    
    bot.send_message(user_id, admins_message)
    log_message(message)

@bot.message_handler(commands=['admin_add'])
def add_admin_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        bot.send_message(user_id, "Only the owner can use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /admin_add [user_id]")
        log_message(message)
        return
    
    if target_id not in admin_list:
        admin_list.append(target_id)
        bot.send_message(user_id, f"User {target_id} added to admins.")
    else:
        bot.send_message(user_id, f"User {target_id} is already an admin.")
    
    log_message(message)

@bot.message_handler(commands=['admin_remove'])
def remove_admin_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        bot.send_message(user_id, "Only the owner can use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /admin_remove [user_id]")
        log_message(message)
        return
    
    if target_id == OWNER_ID:
        bot.send_message(user_id, "The owner cannot be removed from admins.")
    elif target_id in admin_list:
        admin_list.remove(target_id)
        bot.send_message(user_id, f"User {target_id} removed from admins.")
    else:
        bot.send_message(user_id, f"User {target_id} is not an admin.")
    
    log_message(message)
    
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['users'])
def users_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
            
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to access this command.")
        log_message(message)
        return
            
    users_info = []
    for target_id in user_list:
        try:
            user = bot.get_chat(target_id)
            user_name = user.first_name
        except Exception as e:
            user_name = "Unknown User"
                
        if target_id in banned_users:
            users_info.append(f"👤 {user_name} (🆔 {target_id}) ❌")  
        else:
            users_info.append(f"👤 {user_name} (🆔 {target_id})")  
           
    users_message = (
        f"👥 List of Users:\n{'\n'.join(users_info)}\n\n"
        "To manually add a user, use:\n"
        "/user_manual_add [user_id]\n\n"
        "To ban a user, use:\n"
        "/user_ban [user_id]\n\n"
        "To unban a user, use:\n"
        "/user_unban [user_id]"
    )
           
    bot.send_message(user_id, users_message)
    log_message(message)

@bot.message_handler(commands=['user_manual_add'])
def user_manual_add_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id != OWNER_ID:
        bot.send_message(user_id, "You do not have permission to use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /user_manual_add [user_id]")
        log_message(message)
        return
    
    if target_id not in user_list:
        user_list.append(target_id)
        bot.send_message(user_id, f"User {target_id} added to the user list.")
    else:
        bot.send_message(user_id, f"User {target_id} is already in the user list.")
    
    log_message(message)

@bot.message_handler(commands=['user_ban'])
def user_ban_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1]) 
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /user_ban [user_id]")
        log_message(message)
        return
    
    if target_id not in banned_users:
        if target_id not in admin_list:
            banned_users.append(target_id)
            bot.send_message(user_id, f"User {target_id} has been banned.")
        else:
            if user_id == OWNER_ID:
                banned_users.append(target_id)
                bot.send_message(user_id, f"User {target_id} has been banned.")
            else:
                bot.send_message(user_id, "You cannot ban an admin.")
    else:
        bot.send_message(user_id, f"User {target_id} is already banned.")
    
    log_message(message)

@bot.message_handler(commands=['user_unban'])
def user_unban_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])  
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /user_unban [user_id]")
        log_message(message)
        return
    
    if target_id in banned_users:
        if target_id not in admin_list:
            banned_users.remove(target_id)
            bot.send_message(user_id, f"User {target_id} has been unbanned.")
        else:
            if user_id == OWNER_ID:
                banned_users.append(target_id)
                bot.send_message(user_id, f"User {target_id} has been unbanned.")
            else:
                bot.send_message(user_id, "You cannot unban an admin.")
    else:
        bot.send_message(user_id, f"User {target_id} is not banned.")
    
    log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['message'])
def message_command(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in ADMIN_LIST:
        bot.send_message(
            user_id,
            "To send a message to users, use the following command:\n"
            "/send_message [user_id]\n"
            "Or to send to all users:\n"
            "/send_message all"
        )
        log_message(message)
        return
    
    bot.send_message(
        user_id,
        "📨 Send your message.\n"
        "This message will be sent anonymously to the bot developer."
    )
    bot.register_next_step_handler(message, handle_user_message)
    log_message(message)

@bot.message_handler(commands=['send_message'])
def admin_send_message_command(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in ADMIN_LIST:
        bot.send_message(user_id, "You don't have permission to use this command.")
        log_message(message)
        return
    
    try:
        target = message.text.split(maxsplit=1)[1].strip()
        
        if target.lower() == "all":
            msg = bot.send_message(
                user_id,
                "Please send your message now."
            )
            bot.register_next_step_handler(msg, lambda m: handle_admin_message(m, target_users="all"))
        else:
            try:
                target_id = int(target)
                msg = bot.send_message(
                    user_id,
                    "Please send your message now."
                )
                bot.register_next_step_handler(msg, lambda m: handle_admin_message(m, target_users=[target_id]))
            except ValueError:
                bot.send_message(user_id, "User ID must be a number or use 'all'")
                log_message(message)
                return
        
    except IndexError:
        bot.send_message(user_id, "Invalid format. Please use:\n/send_message [user_id]\nor\n/send_message all")
    log_message(message)

def handle_admin_message(message, target_users):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in ADMIN_LIST:
        bot.send_message(user_id, "You don't have permission to use this command.")
        log_message(message)
        return
    
    success_count = 0
    failed_count = 0
    error_msg = ""
    
    if target_users == "all":
        for target_id in USER_LIST:
            if target_id not in BANNED_USERS and target_id != user_id:
                try:
                    bot.copy_message(
                        chat_id=target_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    success_count += 1
                except Exception as e:
                    error_msg = str(e)
                    failed_count += 1
    else:
        for target_id in target_users:
            if target_id not in BANNED_USERS and target_id != OWNER_ID:
                try:
                    bot.copy_message(
                        chat_id=target_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    success_count += 1
                except Exception as e:
                    error_msg = str(e)
                    failed_count += 1
    
    if target_users == "all":
        report_msg = f"✅ Message successfully sent to {success_count} users."
        if failed_count > 0:
            report_msg += f"\n❌ Failed to send to {failed_count} users. Error: {error_msg}"
    else:
        if success_count > 0:
            report_msg = "✅ Message sent successfully."
        else:
            report_msg = f"❌ Failed to send message. Error: {error_msg}"
    
    bot.send_message(
        user_id,
        report_msg
    )
    
    log_message(message)

def handle_user_message(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    try:
        log_msg = f"📨 New message received from user:\n🆔 ID: {user_id}"
        bot.send_message(chat_id=OWNER_ID, text=log_msg)
        bot.forward_message(chat_id=OWNER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        
        bot.send_message(
            user_id,
            "✅ Your message was sent successfully."
        )
        
    except Exception as e:
        bot.send_message(user_id, f"❌ Error sending message. Please try again. Error: {e}")
    
    log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['reminder'])
def reminder_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in admin_list:
        food_reminder_menu = (
            "🍱 Food Reminder Commands (Admin):\n\n"
            "➕ /subscribe_reminder - Add yourself to reminders\n"
            "➖ /unsubscribe_reminder - Remove yourself from reminders\n"
            "📜 /reminder_list - View all users in reminder list\n"
            "👤 /add_to_reminder [user_id] - Add a user to reminders\n"
            "🚫 /remove_from_reminder [user_id] - Remove a user from reminders"
        )
    else:
        food_reminder_menu = (
            "🍱 Food Reminder Commands:\n\n"
            "➕ /subscribe_reminder - Get food reminders\n"
            "➖ /unsubscribe_reminder - Stop getting reminders"
        )

    bot.send_message(user_id, food_reminder_menu)
    log_message(message)

@bot.message_handler(commands=['subscribe_reminder'])
def add_to_reminder_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in reminder_list:
        reminder_list.append(user_id)
        bot.send_message(user_id, "You have been added to the food reminder list.")
    else:
        bot.send_message(user_id, "You are already in the food reminder list.")
    
    log_message(message)

@bot.message_handler(commands=['unsubscribe_reminder'])
def stop_reminder_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id in reminder_list:
        reminder_list.remove(user_id)
        bot.send_message(user_id, "You have been removed from the food reminder list.")
    else:
        bot.send_message(user_id, "You are not in the food reminder list.")
    
    log_message(message)

@bot.message_handler(commands=['reminder_list'])
def show_reminder_list_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to access this command.")
        log_message(message)
        return
    
    reminder_info = []
    for target_id in reminder_list:
        try:
            chat = bot.get_chat(target_id)
            reminder_info.append(f"👤 {chat.first_name} (🆔 {target_id})")
        except Exception as e:
            reminder_info.append(f"👤 Unknown User (🆔 {target_id})")
    
    reminder_message = (
        "📜 Reminder List:\n" + "\n".join(reminder_info) + "\n\n"
        "To add a user to the reminder list, use:\n"
        "/add_to_reminder [user_id]\n\n"
        "To remove a user from the reminder list, use:\n"
        "/remove_from_reminder [user_id]"
    )
    
    bot.send_message(user_id, reminder_message)
    log_message(message)

@bot.message_handler(commands=['add_to_reminder'])
def add_to_reminder_admin_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /add_to_reminder [user_id]")
        log_message(message)
        return
    
    if target_id not in reminder_list:
        reminder_list.append(target_id)
        bot.send_message(user_id, f"User {target_id} has been added to the reminder list.")
    else:
        bot.send_message(user_id, f"User {target_id} is already in the reminder list.")
    
    log_message(message)

@bot.message_handler(commands=['remove_from_reminder'])
def remove_from_reminder_admin_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return

    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to use this command.")
        log_message(message)
        return
    
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(user_id, "Invalid format. Use: /remove_from_reminder [user_id]")
        log_message(message)
        return
    
    if target_id in reminder_list:
        reminder_list.remove(target_id)
        bot.send_message(user_id, f"User {target_id} has been removed from the reminder list.")
    else:
        bot.send_message(user_id, f"User {target_id} is not in the reminder list.")
    
    log_message(message)

def send_reminders():
    while True:
        now = datetime.now(time_zone)
        if now.weekday() == 2 and 22 <= now.hour < 23:
            for user_id in reminder_list:
                try:
                    bot.send_message(user_id, "🍽 رزرو غذا فراموش نشه!")
                except Exception as e:
                    print(f"Error sending reminder to {user_id}: {e}")
            time.sleep(7 * 24 * 3600) 
        else:
            time.sleep(3600)

reminder_thread = threading.Thread(target=send_reminders)
reminder_thread.daemon = True
reminder_thread.start()

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

CRYPTO_COMMANDS = {'/btc': 'BTC', '/eth': 'ETH', '/usdt': 'USDT', '/xrp': 'XRP', '/bnb': 'BNB', '/sol': 'SOL', '/usdc': 'USDC', '/doge': 'DOGE', '/ada': 'ADA', '/trx': 'TRX', '/link': 'LINK', '/ton': 'TON'}
CRYPTOS = {"BTC": "₿", "ETH": "Ξ", "USDT": "💵", "XRP": "✕", "BNB": "ⓑ", "SOL": "◎", "USDC": "💲", "DOGE": "🐶", "ADA": "🅰", "TRX": "🅿", "LINK": "🔗", "TON": "⚡"}
CR_CMDS = ['btc', 'eth', 'usdt', 'xrp', 'bnb', 'sol', 'usdc', 'doge', 'ada', 'trx', 'link', 'ton']

@bot.message_handler(commands=['coin'])
def coin_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return

    if user_id in admin_list:
        coin_menu = "💰 Coin Commands (Admin):\n\n"
    else:
        coin_menu = "💰 Coin Commands:\n\n"
        
    coin_menu += "📊 Quick Price Check Commands:\n"
    for cmd, crypto in CRYPTO_COMMANDS.items():
        emoji = CRYPTOS.get(crypto, "")
        coin_menu += f"{emoji} {cmd} - Check {crypto} price\n"
    
    coin_menu += "\n🔧 General Commands:\n"
    coin_menu += "/how_to_set_api_key - How to get API key\n"
    
    if user_id in admin_list:
        coin_menu += "\n👑 Admin Commands:\n"
        coin_menu += "/api_list - View all registered API keys\n"
    
    bot.send_message(user_id, coin_menu)
    log_message(message)

@bot.message_handler(commands=['set_api_key'])
def set_api_key_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    try:
        api_key = message.text.split(maxsplit=1)[1] 
    except IndexError:
        bot.send_message(user_id, "Invalid format. Use: /set_api_key [api_key]")
        return
    cmc_api_keys[str(user_id)] = api_key
    bot.send_message(user_id, "Your API Key has been set successfully!")
    log_message(message)
    
@bot.message_handler(commands=CR_CMDS)
def handle_crypto_selection(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    api_key = cmc_api_keys.get(str(user_id))
    if not api_key or api_key == "" or api_key == "nan" or pd.isna(api_key):
        bot.send_message(user_id, "You need to set your CoinMarketCap API Key first. /how_to_set_api_key")
        log_message(message)
        return
    
    command = message.text.split()[0].lower()
    crypto = CRYPTO_COMMANDS[command]
    
    try:
        price = fetch_crypto_price(api_key, crypto)
        bot.send_message(user_id, f"The current price of {crypto} is ${price}.")
    except Exception as e:
        bot.send_message(user_id, f"Failed to fetch price for {crypto}: {str(e)}")
    
    log_message(message)

def fetch_crypto_price(api_key: str, crypto: str):
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

@bot.message_handler(commands=['how_to_set_api_key'])
def how_to_set_api_key_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
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
    
    bot.send_message(user_id, help_message)
    log_message(message)

@bot.message_handler(commands=['api_list'])
def show_apis_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "You do not have permission to access this command.")
        log_message(message)
        return
    
    apis_info = []
    for target_id, api_key in cmc_api_keys.items():
        if pd.isna(api_key) or str(api_key).strip() == "":
            continue 
        try:
            user = bot.get_chat(int(target_id))
            apis_info.append(f"👤 {user.first_name} (🆔 {target_id}): {api_key}")
        except Exception as e:
            apis_info.append(f"👤 Unknown User (🆔 {target_id}): {api_key}")
    
    apis_message = "📜 List of APIs:\n" + "\n".join(apis_info)
    bot.send_message(user_id, apis_message)
    log_message(message)

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

@bot.message_handler(commands=['database'])
def handle_database_command(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    
    if user_id not in admin_list:
        bot.send_message(user_id, "❌ Only admins can access this command")
        log_message(message)
        return
    
    success = db.export_database(
        bot=bot,
        chat_id=message.from_user.id,
        user_list=user_list,
        admin_list=admin_list,
        banned_users=banned_users,
        reminder_list=reminder_list,
        cmc_api_keys=cmc_api_keys
    )
    if not success:
        bot.send_message(user_id, "❌ Failed to export database")
    
    log_message(message)
    
@bot.message_handler(func=lambda message: True)
def forward_all_messages(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.send_message(user_id, "You have been banned from the bot. Message the developer to unban.")
        return
    log_message(message)
    
try:
    print("Bot is on fire...") 
    bot.send_message(OWNER_ID, "🤖 Bot is on fire...")
    bot.infinity_polling()
except Exception as e:
    print(f"Error in deployment: {e}")
    bot.send_message(OWNER_ID, f"⚠️ failed to deploy. Error: {e}")
