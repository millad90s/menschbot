from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import sqlite3
from datetime import datetime
import json
import random, os

# Database initialization
def init_database():
    print("Initializing database...")
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  language_code TEXT,
                  join_date TEXT,
                  last_active TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_interactions
                 (user_id INTEGER,
                  message_id INTEGER,
                  message_type TEXT,
                  message_content TEXT,
                  timestamp TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

# Help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested help.".format(update.effective_user.first_name))
    await update.message.reply_text("I can help you learn 504 essential words daily.\n"
                                    "- /help to get this help message\n"
                                    "- /start to start learning\n"
                                    "- /word to get a random 504 word\n\n"
                                    "Your data helps personalize your learning experience.")
    
# Basic user information collection
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} started the conversation.".format(update.effective_user.first_name))
    # await update.message.reply_text("Welcome! I’m here to help you learn 504 essential words. Type /word to get started!")
    user = update.effective_user
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code
    }
    
    # Store user data
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO users 
                 (user_id, username, first_name, last_name, language_code, join_date)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_data['user_id'], user_data['username'], 
               user_data['first_name'], user_data['last_name'],
               user_data['language_code'], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    welcome_message = (
        f"Welcome {user.first_name}!\n\n"
        "I can help you learn while collecting:\n"
        "- Basic profile information\n"
        "- Language preference\n"
        "- Learning progress\n"
        "- Usage statistics\n\n"
        "Your data helps personalize your learning experience."
    )
    
    keyboard = [
        [InlineKeyboardButton("Start Learning", callback_data='start_learning')],
        [InlineKeyboardButton("View My Data", callback_data='view_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

### select a randorm item from 504_words.json and send it to the user
async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested a word.".format(update.effective_user.first_name))
    # Load words from JSON
    with open("504_words.json", "r") as file:
        words_data = json.load(file)
        word=random.choice(words_data)
        print(word)
        await update.message.reply_text(
            f"Word: {word['word']}\nDefinition: {word['definition']}\nExample: {word['example']}")
        
            
    
    
# Track user interactions
async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} sent message: {}".format(update.effective_user.first_name, update.message.text))
    user = update.effective_user
    message = update.message
    
    # Store message interaction
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO user_interactions 
                 (user_id, message_id, message_type, message_content, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
              (user.id, message.message_id, 
               message.content_type, message.text, 
               datetime.now().isoformat()))
    
    # Update last active timestamp
    c.execute('''UPDATE users 
                 SET last_active = ? 
                 WHERE user_id = ?''',
              (datetime.now().isoformat(), user.id))
    
    conn.commit()
    conn.close()
    
    await update.message.reply_text("Message received!")

# Show user their collected data
async def show_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested user data.".format(update.effective_user.first_name))
    user = update.effective_user
    
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    # Get user profile data
    c.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
    user_data = c.fetchone()
    
    # Get interaction statistics
    c.execute('''SELECT 
                 COUNT(*) as message_count,
                 MAX(timestamp) as last_interaction
                 FROM user_interactions 
                 WHERE user_id = ?''', (user.id,))
    stats = c.fetchone()
    
    conn.close()
    
    if user_data:
        message = (
            "📊 Your Profile Data:\n\n"
            f"User ID: {user_data[0]}\n"
            f"Username: {user_data[1]}\n"
            f"First Name: {user_data[2]}\n"
            f"Last Name: {user_data[3]}\n"
            f"Language: {user_data[4]}\n"
            f"Join Date: {user_data[5]}\n"
            f"Last Active: {user_data[6]}\n\n"
            f"Total Messages: {stats[0]}\n"
            f"Last Interaction: {stats[1]}"
        )
    else:
        message = "No data found for your profile."
    
    await update.callback_query.edit_message_text(message)

def main():
    # Initialize database
    init_database()
    
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("word", word))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))
    application.add_handler(CallbackQueryHandler(show_user_data, pattern='^view_data$'))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()