from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from chatgpt_module import gpt_en_words_definition
import schedule
import requests
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import sqlite3
from datetime import datetime, timedelta
import json
import random, os
import logging
import urllib.request


### set which language to want to learn , English or Deutsch 
keyboard_setting_level = [
    [
        InlineKeyboardButton("Easy 🇬🇧", callback_data='easy_level'),
        InlineKeyboardButton("mid 🇩🇪", callback_data='deutscmid_level'),
        InlineKeyboardButton("Hard 🇬🇧", callback_data='hard_level')
    ],
    [
        InlineKeyboardButton("Sport", callback_data='Sport'),
        InlineKeyboardButton("Health", callback_data='Health'),
        InlineKeyboardButton("Tech", callback_data='Tech')
    ],
    [
        InlineKeyboardButton("Back", callback_data='Back_menu'),
        InlineKeyboardButton("Confirm", callback_data='Setting_confirm'),
    ]
]
keyboard = [
    [
        InlineKeyboardButton("Word 🤓 ", callback_data='word'),
        InlineKeyboardButton("quiz 💯 ", callback_data='quiz')
    ],
    # [
    #     InlineKeyboardButton("Grammar 🤓 ", callback_data='grammar'),
    #     InlineKeyboardButton("Quiz 🤓 ", callback_data='Quiz')
    # ],
    [
        InlineKeyboardButton("News 📰", callback_data='news') ,
        InlineKeyboardButton("Podcast 🤓", callback_data='podcast')
    ],
    # [
    #     InlineKeyboardButton("Setting 💯", callback_data='setting')
    # ],
    [InlineKeyboardButton("Donate 😍", callback_data='donate', url="https://paypal.me/millad90s?country.x=DE&locale.x=en_US")]
]
    
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

### set user settingin database
def set_user_settings(user_id : int, language : str):
    try:
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('UPDATE users SET language_code = ? WHERE user_id = ?', (language, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    

### get a podcast url
def get_podcast_url():
    with open("504_words_v2.json", "r") as file:
        data = json.load(file)
        lesson = random.choice(data["lessons"])
        lesson_url  = lesson["podcast_url"]
        return lesson_url, lesson["lesson_number"]
    
### get a random word
def get_a_word():
    with open("504_words_v2.json", "r") as file:
        data = json.load(file)
        lesson = random.choice(data["lessons"])
        word  = random.choices(lesson["words"])
        return word
    
### get two random words with definition
### Todo : get three random unique words 
def get_three_words():
    with open("504_words_v2.json", "r") as file:
        data = json.load(file)
        lesson = random.choice(data["lessons"])
        word1  = random.choice(lesson["words"])
        word2  = random.choice(lesson["words"])
        word3  = random.choice(lesson["words"])
        return [word1, word2, word3]
    
    
### send a audiofile to users
async def podcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested audio.".format(update.effective_user.first_name))
    print(update.message)
    my_url, lesson_number = get_podcast_url()
    audio_file = urllib.request.urlopen(my_url)

    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio_file, title="504 Lesson "+str(lesson_number), thumbnail='https://englishpodcast.fra1.cdn.digitaloceanspaces.com/504/504_podcast.jpeg', caption="Podcast by Platform124", protect_content=True )
    
### handle grammar menu and show grammar keyboard
async def grammar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested grammar.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Comming Soon", reply_markup=reply_markup)
    

### handle grammar_quiz menu and show grammar keyboard
async def grammar_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested grammar.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Comming Soon ...", reply_markup=reply_markup)
    
### send a quiz/poll to user from the words
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested quiz.".format(update.effective_user.first_name))
    
    ### get a word
    question_list = get_three_words()
    correct_word  = random.choice(question_list)
    correct_option_id = question_list.index(correct_word)
    await context.bot.send_poll(chat_id=update.effective_chat.id, 
                                question=correct_word['word'], 
                                options=[x['definition'] for x in question_list ],
                                is_anonymous=False, type='quiz',
                                correct_option_id=question_list.index(correct_word),
                                explanation=correct_word['examples'][0])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)
    
    
async def daily_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested daily review.".format(update.effective_user.first_name))
    ### detetct userid from database
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (update.effective_user.id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        print("User {} requested daily review.".format(update.effective_user.first_name))
        news = fetch_news('https://api.mediastack.com/v1/news?access_key='+os.getenv('MEDIASTACK_API_KEY')+'&languages=en')
        if news:
            for article in random.choices(news):
                await update.callback_query.edit_message_text(str(article['author']) + '\n' + article['title'] + '\n\n' + article['url'] + '\n\n' + article['description'])
        else:
            await update.callback_query.edit_message_text("No news found.")
    else:
        await update.message.reply_text("You need to start learning first.")
        
        
def fetch_news(url, date: str = None, categoty: str = 'entertainment'):
    try:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            logging.info(f"Date: {date}")
        # if json file for today is exist then read from json file 
        if os.path.exists(f"news_{date}.json"):
            with open(f"news_{date}.json", "r") as file:
                logging.info(f"news_{date}.json file found")
                news_data = json.load(file)
                return news_data
        else:
            # if json file for today is not exist then fetch the news from api
            complte_url = url # + f"&categories={categoty}" + f"&date={date}"
            # complte_url = url + f"&categories={categoty}" + f"&date=2024-11-05"
            
            response = requests.get(complte_url)
            logging.info(f"News fetched: {response.status_code}")
            data = random.choices(response.json()['data'], k=10)
            if response.status_code == 200 and data.__len__() > 0:
                data2 = [dict(des, teaching=gpt_en_words_definition(des['description'])) for des in data]
                response_json = json.dumps(data2)

                ### store the json in the json file  as list , not string 
                with open(f"news_{date}.json", "w") as file:
                    logging.info(f"news_{date}.json file created")
                    
                    file.write(response_json)
                    news_data = json.load(file)
                    return news_data

            elif response.json()['data'].__len__() == 0:
                logging.info(f"No news found for date: {date}")
                ### read news from yesterday if there is no news for today
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                try:
                    with open(f"news_{yesterday}.json", "r") as file:
                        news_data = json.load(file)
                        return news_data
                except Exception as e:
                    print(f"An error occurred: {e}")
                    return [{"author": "No news found.", "title": "No news found.", "url": "No news found.", "description": "No news found. "}]
                
            else:
                print(f"Failed to fetch news. Status code: {response.status_code}")
                return [{"author": "No news found.", "title": "No news found.", "url": "No news found.", "description": "No news found. "}]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
# Basic user information collection
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {}  by ID {} started the conversation.".format(update.effective_user.first_name, update.effective_user.id) )
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
    


    # welcome_message = (
    #     f"Welcome {user.first_name}!\n\n"
    #     "I can help you learn while collecting:\n"
    #     "- Basic profile information\n"
    #     "- Language preference\n"
    #     "- Learning progress\n"
    #     "- Usage statistics\n\n"
    #     "Your data helps personalize your learning experience."
    # )
    
    # keyboard = [
    #     [InlineKeyboardButton("Get a Word", callback_data='word'),
    #      InlineKeyboardButton("News", callback_data='news') ],
    #     [InlineKeyboardButton("View My status", callback_data='view_data') ],
    #     [InlineKeyboardButton("Donate 😍", callback_data='donate', url="https://paypal.me/millad90s?country.x=DE&locale.x=en_US")]
    # ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Select an option:", reply_markup=reply_markup)

### select a randorm item from 504_words.json and send it to the user
async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested a word.".format(update.effective_user.first_name))
    word  = get_a_word()
        
    await update.message.reply_text(f"Word: {word['word']}\nDefinition: {word['definition']}\nPhonetic: {word['phonetic']}\n\nExample: {word['examples'][0]}")
        
    # Load words from JSON
    # with open("504_words.json", "r") as file:
    #     words_data = json.load(file)
    #     word=random.choice(words_data)
    #     print(word)
    #     await update.message.reply_text(
    #         f"Word: {word['word']}\nDefinition: {word['definition']}\nExample: {word['example']}")

    
### handle admin_sen_allow , admin can send a message to all users
async def admin_sen_allow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ### check if it's coming from admin id 
    print("User {} requested help.".format(update.effective_user.first_name))
    if str(update.effective_user.id) != os.getenv('ADMIN_ID'):
        await update.message.reply_text("You are not allowed to use this command.")
    else:
    ### read all users id from database 
        conn = sqlite3.connect(os.getenv('DB_PATH'))
        c = conn.cursor()
        c.execute("SELECT user_id, first_name FROM users")
        users = c.fetchall()
        conn.close()
        for user in users:
            try:
                await context.bot.send_message(chat_id=user[0], text=f"""Dear user {user[1]} , Admin sent you a message:\n\n{update.message.text.split(maxsplit=1)[1]}""") #    update.message.text)
            except Exception as e:
                print(f"Error sending message to user {user[0]}: {e}")
            
            
# Track user interactions
async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} sent message: {}".format(update.effective_user.first_name, update.message.text))
    user = update.effective_user
    message = update.message
    
    # Store message interaction
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    try:
        # Store message
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
    except AttributeError:
        print("Message is not text.")
    
    conn.commit()
    conn.close()
    
    print("User {} requested help.".format(update.effective_user.first_name))
    await update.message.reply_text("I can help you learn 504 essential words daily.\n"
                                    "- /help to get this help message\n"
                                    "- /start to start learning\n"
                                    "- /word to get a random 504 word\n\n"
                                    "Your data helps personalize your learning experience.")



async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} donated.".format(update.effective_user.first_name))
    donation_text = "Thanks for your donation!\n\n https://paypal.me/millad90s?country.x=DE&locale.x=en_US"
        
    await update.callback_query.edit_message_text(donation_text)
    
async def start_learning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} started learning.".format(update.effective_user.first_name))
    
    word  = get_a_word()[0]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Word: {word['word']}\nDefinition: {word['definition']}\nPhonetic: {word['phonetic']}\n\nExample1: {word['examples'][0]} \n\nExample2: {word['examples'][1]} " + f"\n\n🗻🗻🗻🗻🗻")
    # await update.message.reply_text(f"Word: {word['word']}\nDefinition: {word['definition']}\nPhonetic: {word['phonetic']}\n\nExample: {word['examples'][0]}")
     
    
    
async def handle_user_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} handle_user_setting".format(update.effective_user.first_name))
    ### set user settingin database by calling function 
    set_user_settings(update.effective_user.id, 'en')
    await update.callback_query.edit_message_text("Language set to English.")
    
### handle Setting menu and show settings keyboard 
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested settings.".format(update.effective_user.first_name))
    # Get the chat ID
    chat_id = update.effective_chat.id
    # Send the menu
    await context.bot.send_message(
        chat_id=chat_id,
        text="Select a language:",
        reply_markup=InlineKeyboardMarkup(keyboard_setting_level)
    )
async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested news.".format(update.effective_user.first_name))
    news = fetch_news('https://api.mediastack.com/v1/news?access_key='+os.getenv('MEDIASTACK_API_KEY')+'&languages=en')
    new  = random.choice(news)
    author = str(new.get("author", "Anonymous"))
    title = str(new.get("title", "No title"))
    news_url = str(new.get("url", "No URL"))
    description = str(new.get("description", "No description"))
    teaching = str(new.get("teaching", "No teaching"))
    await update.callback_query.edit_message_text( author + '\n' + title + '\n\n' + news_url + '\n\n' + description + "\n\n" + teaching)
    # Get the chat ID
    chat_id = update.effective_chat.id
   # Send the menu again
    await context.bot.send_message(
        chat_id=chat_id,
        text="Select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Show user their collected data
async def show_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested user data.".format(update.effective_user.first_name))
    user = update.effective_user
    
    # conn = sqlite3.connect('user_data.db')
    # c = conn.cursor()
    
    # # Get user profile data
    # c.execute('SELECT * FROM users WHERE user_id = ?', (user.id,))
    # user_data = c.fetchone()
    
    # # Get interaction statistics
    # c.execute('''SELECT 
    #              COUNT(*) as message_count,
    #              MAX(timestamp) as last_interaction
    #              FROM user_interactions 
    #              WHERE user_id = ?''', (user.id,))
    # stats = c.fetchone()
    
    # conn.close()
    
    # if user_data:
    #     message = (
    #         "📊 Your Profile Data:\n\n"
    #         f"User ID: {user_data[0]}\n"
    #         f"Username: {user_data[1]}\n"
    #         f"First Name: {user_data[2]}\n"
    #         f"Last Name: {user_data[3]}\n"
    #         f"Language: {user_data[4]}\n"
    #         f"Join Date: {user_data[5]}\n"
    #         f"Last Active: {user_data[6]}\n\n"
    #         f"Total Messages: {stats[0]}\n"
    #         f"Last Interaction: {stats[1]}"
    #     )
    # else:
    #     message = "No data found for your profile."
    
    # await update.callback_query.edit_message_text(message)
    
    chat_id = update.effective_chat.id
   # Send the menu again
    await context.bot.send_message(
        chat_id=chat_id,
        text="Select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    # Initialize database
    init_database()
    
    # Load environment variables
    load_dotenv()
    
    ### setup logger
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    print(os.getenv("TELEGRAM_API_KEY")[-5:])
    
    # read NEWS_URL variable from .env
    NEWS_URL = os.getenv("NEWS_URL")
    
    # read MEDIASTACK_API_KEY variable from .env
    MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY") 
        
    application = Application.builder().token(os.getenv("TELEGRAM_API_KEY")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("word", word))
    application.add_handler(CommandHandler("admin_send_all", admin_sen_allow))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))
    application.add_handler(CallbackQueryHandler(show_user_data, pattern='^view_data$'))
    application.add_handler(CallbackQueryHandler(start_learning, pattern='^word$'))
    application.add_handler(CallbackQueryHandler(donate, pattern='^donate$'))
    application.add_handler(CallbackQueryHandler(daily_review, pattern='^daily_review$'))
    application.add_handler(CallbackQueryHandler(get_news, pattern='^news$'))
    application.add_handler(CallbackQueryHandler(settings, pattern='^setting$'))
    application.add_handler(CallbackQueryHandler(podcast, pattern='^podcast$'))
    application.add_handler(CallbackQueryHandler(quiz, pattern='^quiz$'))
    application.add_handler(CallbackQueryHandler(grammar, pattern='^grammar$'))
    application.add_handler(CallbackQueryHandler(grammar_quiz, pattern='^grammar_quiz$'))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()