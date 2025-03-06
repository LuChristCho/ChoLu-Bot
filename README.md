# 🤖 ChoLu 2.6 - Telegram Bot

ChoLu 2.6 is a smart and multi-purpose Telegram bot designed for user management, sending reminders, collecting feedback, and displaying cryptocurrency prices. It is fully customizable and can be used for various purposes.

---

## ✨ Features

- **User Management**: Add, remove, and view the list of users.
- **Reminders**: Automatically send food reservation reminders every Wednesday between 9 PM and 11 PM.
- **Feedback Collection**: Collect anonymous feedback from users.
- **Admin Management**: Add, remove, and view the list of admins.
- **Cryptocurrency Prices**: Get real-time prices of cryptocurrencies like Bitcoin, Ethereum, Tether, and more.
- **Broadcast Messages**: Send messages to all users or specific users.

---

## 🚀 Getting Started

### 1. Prerequisites
- Create a Telegram bot using [BotFather](https://t.me/BotFather) and obtain the bot token.
- Get your API key from [CoinMarketCap](https://coinmarketcap.com/api/).

### 2. Installation and Setup

#### 2.1. Install Required Libraries
Install the required libraries using the following command:

```bash
pip install -r requirements.txt
```

#### 2.2. Set Up Environment Variables
Create a `.env` file in the root directory and add the following information:

```env
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
USER_LIST=user_ids_separated_by_commas
FOOD_RESERVATION_LIST=user_ids_separated_by_commas
TIMEZONE=your_timezone
```

#### 2.3. Run the Bot
Start the bot using the following command:

```bash
python bot.py
```

---

## 🛠 Bot Commands

### General Commands
- `/start`: Start the bot and get basic information.
- `/help`: Show the list of available commands.
- `/feedback`: Send anonymous feedback to the admin.
- `/requestforreservation`: Request to be added to the food reservation list.
- `/coin`: Get cryptocurrency prices.

### Admin Panel
- `/myadmins`: View the list of admins.
- `/adminmanager`: Manage admins (add, remove, or clear the admin list).
- `/forcemessage`: Send a message to all users or specific users.
- `/printusers`: View the list of users.
- `/adduser`: Add a user to the user list.
- `/printreservation`: View the list of users on the food reservation list.

---

## 🛡 Security

- **Environment Variables**: Sensitive information like the bot token and API keys are stored in the `.env` file and are not exposed in the code.
- **Feedback Limit**: Each user can send a maximum of 15 feedback messages per day.

---

## 🤝 Contributing

If you'd like to contribute to the development of this bot, follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push your changes (`git push origin feature/YourFeatureName`).
5. Create a Pull Request.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📞 Contact the Developer

If you have any questions or need assistance, feel free to reach out to me on [Telegram](https://t.me/masihssj).

---

**Enjoy using ChoLu 2.6!** 🎉

---
