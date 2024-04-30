# Telegram Chatbot with OpenAI Integration

This Telegram bot is designed to assist users with managing their expenses and providing responses based on user input using OpenAI's GPT-4 model.

## Features:
- **User Registration**: Upon starting a conversation with the bot, users are automatically registered in the database.
- **Expense and Income Tracking**: Users can add records of their expenses and incomes using simple commands.
- **History Display**: Users can view their expense and income history for a specified time period.
- **Help Command**: Users can access help information by using the `/help` command.

## Prerequisites

Before you run the code, make sure you have the following:

- Python 3.6 or higher installed on your system.
- Telegram API token for your bot.
- OpenAI API key.

## Installation

1. **Clone this repository:**
   
   ```bash
   git clone git@github.com:nup-csai/Telegram-bot-for-calculating-total-expenses.git
   
2. **Install the required dependencies:**
   
   ```bash
   pip install -r requirements.txt

3. **Create a .env file in the root directory and add your OpenAI API key and put your Telegram API token:**

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   TELEGRAM_API_TOKEN = "your_telegram_api_token"```

# Telegram Bot Token Acquisition Guide

This guide outlines the steps to obtain a Telegram Bot Token for creating and managing a bot on the Telegram platform.

### Prerequisites
- A Telegram account.
- Access to the Telegram platform either through the web or the mobile app.

### Steps to Obtain Telegram Bot Token:

1. **Create a Telegram Bot**:
   - Start a conversation with [@BotFather](https://t.me/BotFather) on Telegram.
   - Type `/start` to initiate the conversation.
   - Follow the on-screen instructions to create a new bot.
   - You will need to provide a name for your bot and receive a unique username for it.

2. **Obtain Bot Token**:
   - After successfully creating the bot, [@BotFather](https://t.me/BotFather) will provide you with an API token.
   - This token is your bot's access key and is essential for communicating with the Telegram Bot API.

3. **Save Your Token**:
   - Copy the provided API token. This you need to use in your .env file
   
## Usage
Run the Python script 'app.py':
   ```bash
   python app.py
```

## Bot commands:
1. Start the bot by sending the `/start` command.
2. Use the `/spent` or `/s` command followed by the amount to add an expense record.
3. Use the `/earned` or `/e` command followed by the amount to add an income record.
4. Use the `/history` or `/h` command to view your expense and income history.
5. Use the `/help` command to access help information.
6. Write a message to recieve an answer from OpenAi

## Additional Notes:
- Ensure that your bot token is correctly set in the `app.py` file.
- The bot uses SQLite3 as the database backend. Ensure that you have the necessary permissions to create and write to the database file.

