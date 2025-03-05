import telebot
from telebot.types import ChatMemberUpdated
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
USER_LIST = list(map(int, os.getenv("USER_LIST").split(',')))
FOOD_RESERVATION_LIST = list(map(int, os.getenv("FOOD_RESERVATION_LIST").split(',')))

bot = telebot.TeleBot(BOT_TOKEN)
bot_admins = [OWNER_ID]
user_list = USER_LIST
food_reservation_list = FOOD_RESERVATION_LIST
user_feedback_count = {}
scheduler = BackgroundScheduler()


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    bot.reply_to(message, "Welcome to ChoLu 2.6! Type /help for more information.")
    
    if user_id != OWNER_ID:
        if user_id not in user_list:
            user_list.append(user_id)
        bot.send_message(
            OWNER_ID,
            f"🚀 A new user has started the bot:\n"
            f"👤 Name: {user_name}\n"
            f"🆔 ID: {user_id}"
        )


@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(
            message,
            "/start to restart bot for apply last updates.\n"
            "/myadmins to view bot administrators.\n"
            "/adminmanager to remove or add admins.\n"
            "/forcemessage to send messages for bot users.\n"
            "/printusers to list all users.\n"
            "/adduser to manually add a user ID.\n"
            "/coin to get cryptocurrency prices.\n"
            "/printreservation to list users on the food reservation list.\n"
            "/requestforreservation to request to be added to the food reservation list."
        )
    elif message.from_user.id in bot_admins:
        bot.reply_to(
            message,
            "/start to restart bot for apply last updates.\n"
            "/myadmins to view bot administrators.\n"
            "/feedback to anonymously send your feedback.\n"
            "/coin to get cryptocurrency prices.\n"
            "/requestforreservation to request to be added to the food reservation list."
        )
    else:
        bot.reply_to(
            message,
            "/start to restart bot for apply last updates.\n"
            "/feedback to anonymously send your feedback.\n"
        )


@bot.message_handler(commands=['myadmins'])
def list_admins(message):
    if message.from_user.id in bot_admins:
        admin_names = []
        for admin_id in bot_admins:
            try:
                user = bot.get_chat(admin_id)
                admin_names.append(f"{user.first_name} (ID: {admin_id})")
            except Exception as e:
                admin_names.append(f"ID: {admin_id} (Unable to fetch name: {e})")

        bot.reply_to(message, "Bot administrators:\n" + "\n".join(admin_names))
    else:
        bot.reply_to(message, "You are not authorized to use this command.")
        
        
@bot.message_handler(commands=['adminmanager'])
def admin_manager(message):
    if message.from_user.id == OWNER_ID:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "Invalid command. Use one of the following:\nadd [numerical ID]\nremove [numerical ID]\nempty")
            return

        command = command_parts[1].lower()
        if command == "add" and len(command_parts) == 3:
            try:
                admin_id = int(command_parts[2])
                if admin_id not in bot_admins:
                    bot_admins.append(admin_id)
                    bot.reply_to(message, f"ID {admin_id} has been added to the admin list.")
                else:
                    bot.reply_to(message, f"ID {admin_id} is already an admin.")
            except ValueError:
                bot.reply_to(message, "Invalid numerical ID.")

        elif command == "remove" and len(command_parts) == 3:
            try:
                admin_id = int(command_parts[2])
                if admin_id in bot_admins and admin_id != OWNER_ID:
                    bot_admins.remove(admin_id)
                    bot.reply_to(message, f"ID {admin_id} has been removed from the admin list.")
                else:
                    bot.reply_to(message, f"ID {admin_id} is not an admin or cannot be removed.")
            except ValueError:
                bot.reply_to(message, "Invalid numerical ID.")

        elif command == "empty" and len(command_parts) == 2:
            bot_admins.clear()
            bot_admins.append(OWNER_ID)
            bot.reply_to(message, "All admins except the owner have been removed.")

        else:
            bot.reply_to(message, "Invalid command. Use one of the following:\nadd [numerical ID]\nremove [numerical ID]\nempty")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")


@bot.message_handler(commands=['printusers'])
def print_users(message):
    if message.from_user.id == OWNER_ID:
        if not user_list:
            bot.reply_to(message, "No users have interacted with the bot yet.")
            return

        user_details = []
        for user_id in user_list:
            try:
                user = bot.get_chat(user_id)
                user_details.append(f"👤 Name: {user.first_name} (ID: {user_id})")
            except Exception as e:
                user_details.append(f"👤 ID: {user_id} (Unable to fetch name: {e})")

        bot.reply_to(message, "List of users:\n" + "\n".join(user_details))
    else:
        bot.reply_to(message, "You are not authorized to use this command.")


@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id == OWNER_ID:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Invalid command. Use /adduser [numerical ID].")
            return

        try:
            user_id = int(command_parts[1])
            if user_id not in user_list:
                user_list.append(user_id)
                bot.reply_to(message, f"User ID {user_id} has been added to the user list.")
            else:
                bot.reply_to(message, f"User ID {user_id} is already in the user list.")
        except ValueError:
            bot.reply_to(message, "Invalid numerical ID.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")
        

@bot.message_handler(commands=['feedback'])
def handle_feedback(message):
    bot.reply_to(message, "Send your feedback (text or media).")
    bot.register_next_step_handler(message, collect_feedback)


def collect_feedback(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    current_time = datetime.now()

    if user_id != OWNER_ID:
        if user_id not in user_feedback_count:
            user_feedback_count[user_id] = {
                "count": 0,
                "reset_time": current_time + timedelta(days=1)
            }
        elif current_time > user_feedback_count[user_id]["reset_time"]:
            user_feedback_count[user_id] = {
                "count": 0,
                "reset_time": current_time + timedelta(days=1)
            }

        if user_feedback_count[user_id]["count"] >= 15:
            bot.reply_to(message, "You have reached your daily limit of 15 feedback messages. Please try again after 24 hours.")
            return

        user_feedback_count[user_id]["count"] += 1

    if message.content_type == 'text':
        bot.reply_to(message, "Thank you for your feedback!")
        bot.send_message(OWNER_ID, f"You have a new feedback message from {user_name} (ID: {user_id}): {message.text}")
    else:
        bot.reply_to(message, "Thank you for your feedback!")
        bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        bot.send_message(OWNER_ID, f"Feedback from {user_name} (ID: {user_id}):")


@bot.message_handler(commands=['forcemessage'])
def force_message_start(message):
    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "Enter the numeric ID (or enter 'all' to send the message to all users of the bot).")
        bot.register_next_step_handler(message, process_recipient)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")


def process_recipient(message):
    recipient = message.text.strip().lower()
    if recipient == "all":
        bot.reply_to(message, "Send the message to be forwarded to all users.")
        bot.register_next_step_handler(message, send_to_all)
    else:
        try:
            recipient_id = int(recipient)
            bot.reply_to(message, f"Send the message to be forwarded to user with ID {recipient_id}.")
            bot.register_next_step_handler(message, lambda msg: send_to_user(msg, recipient_id))
        except ValueError:
            bot.reply_to(message, "Invalid numeric ID. Please restart the /forcemessage command.")


def send_to_user(message, recipient_id):
    try:
        bot.copy_message(recipient_id, message.chat.id, message.message_id)
        bot.reply_to(message, f"Message successfully sent to user with ID {recipient_id}.")
    except Exception as e:
        bot.reply_to(message, f"Failed to send the message: {e}")


def send_to_all(message):
    failed_ids = []
    for user_id in user_list:
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
        except Exception as e:
            failed_ids.append(user_id)

    if failed_ids:
        bot.reply_to(message, f"Message sent to all users except the following IDs: {', '.join(map(str, failed_ids))}.")
    else:
        bot.reply_to(message, "Message successfully sent to all users.")
        
        
@bot.message_handler(commands=['coin'])
def get_crypto_prices(message):
    if message.from_user.id in bot_admins:
        cryptocurrencies = {
            "Bitcoin": "1",
            "Ethereum": "1027",
            "Tether": "825",
            "Doge": "74",
            "Shiba": "5994"
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }

        prices = []
        for name, id in cryptocurrencies.items():
            url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                price = data['data'][id]['quote']['USD']['price']
                prices.append(f"{name}: ${price:.2f}")
            else:
                prices.append(f"{name}: Failed to fetch price")

        bot.reply_to(message, "\n".join(prices))
    else:
        bot.reply_to(message, "You are not authorized to use this command.")
        
        
@bot.message_handler(commands=['printreservation'])
def print_reservation(message):
    if message.from_user.id == OWNER_ID:
        if not food_reservation_list:
            bot.reply_to(message, "No users are on the food reservation list.")
            return

        user_details = []
        for user_id in food_reservation_list:
            try:
                user = bot.get_chat(user_id) 
                user_details.append(f"👤 Name: {user.first_name} (ID: {user_id})")
            except Exception as e:
                user_details.append(f"👤 ID: {user_id} (Unable to fetch name: {e})")

        bot.reply_to(message, "Users on the food reservation list:\n" + "\n".join(user_details))
    else:
        bot.reply_to(message, "You are not authorized to use this command.")


@bot.message_handler(commands=['requestforreservation'])
def handle_request_for_reservation(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if user_id in food_reservation_list:
        bot.reply_to(message, "You are already on the food reservation list.")
    else:
        bot.reply_to(message, "Your request has been sent to the admin.")
        bot.send_message(
            OWNER_ID,
            f"User {user_name} with numeric ID {user_id} requests to be added to the food reservation list reminder.\n"
            f"To agree, /yes\n"
            f"To disagree, /no"
        )

@bot.message_handler(commands=['yes'])
def handle_yes(message):
    if message.from_user.id == OWNER_ID:
        command_parts = message.text.split()
        if len(command_parts) == 2:
            try:
                user_id = int(command_parts[1])
                if user_id not in food_reservation_list:
                    food_reservation_list.append(user_id)
                    bot.reply_to(message, f"User ID {user_id} has been added to the food reservation list.")
                    bot.send_message(user_id, "Your request to be added to the food reservation list has been accepted.")
                else:
                    bot.reply_to(message, f"User ID {user_id} is already on the food reservation list.")
            except ValueError:
                bot.reply_to(message, "Invalid numerical ID.")
        else:
            bot.reply_to(message, "Invalid command. Use /yes [numerical ID].")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")


@bot.message_handler(commands=['no'])
def handle_no(message):
    if message.from_user.id == OWNER_ID:
        command_parts = message.text.split()
        if len(command_parts) == 2:
            try:
                user_id = int(command_parts[1])
                if user_id in food_reservation_list:
                    food_reservation_list.remove(user_id)
                    bot.reply_to(message, f"User ID {user_id} has been removed from the food reservation list.")
                    bot.send_message(user_id, "Your request to be added to the food reservation list has been rejected.")
                else:
                    bot.reply_to(message, f"User ID {user_id} is not on the food reservation list.")
            except ValueError:
                bot.reply_to(message, "Invalid numerical ID.")
        else:
            bot.reply_to(message, "Invalid command. Use /no [numerical ID].")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")
        
def send_reminders():
    now = datetime.now()
    if now.weekday() == 2 and (22 <= now.hour < 24):
        for user_id in food_reservation_list:
            try:
                bot.send_message(user_id, "رزرو غذا فراموش نشه!")
                print(f"Reminder sent successfully to user {user_id}")
            except Exception as e:
                print(f"Failed to send reminder to user {user_id}: {e}")

scheduler.add_job(send_reminders, 'interval', hours=1) 
scheduler.start()

print("Bot is on fire...") 
bot.infinity_polling()