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

3. **Create a .env file in the root directory and add your OpenAI API key:**

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key

4. **In the .config file put your OpenAI API key:**

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key

   
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

