from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from chatgpt_module import gpt_en_words_definition, get_dialog
from news.tagesschauApi import read_news, fetch_videos_news
import schedule
import requests
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    CallbackContext,
    PollAnswerHandler
)
import sqlite3
from datetime import datetime, timedelta
import json
import random, os
import logging
import urllib.request

active_polls = {}
user_navigation_stacks = {}
user_data = {}


todo = [
    "Import All A2 nouns , done to the end of lesson 3 ",
    "Import All A2 verbs , done to the end of lesson 3 ",
    "Import All A2 adjectives , done to the end of lesson 3 ",
    "Find the Stories for A2.2 with Images",
]
keyboards = {
    'main_keyboard': [
        [
            InlineKeyboardButton("⏱️", callback_data='A1.1'),
            InlineKeyboardButton("⏱️", callback_data='A1.2'),
        ],
        [
            InlineKeyboardButton("⏱️", callback_data='A2.1'),
            InlineKeyboardButton("A2.2", callback_data='A2.2'),
        ],
        [
            InlineKeyboardButton("Level Test", callback_data='level_test'),
        ]
    ],
    'keyboard_a22': [
        [
            InlineKeyboardButton("Learn", callback_data='A2.2_learn'),
            InlineKeyboardButton("Quiz", callback_data='A2.2_quiz'),
        ],
        [
            InlineKeyboardButton("News 📺", callback_data='A2.2_news'),
            InlineKeyboardButton("Podcast 🎧", callback_data='A2.2_podcast'),
        ],
        [
            InlineKeyboardButton("Story 🧛", callback_data='a22_story'),
        ],
        [
            InlineKeyboardButton("Back", callback_data='Back_main_menu'),
        ]],
    'keyboard_a22_learn' : [
        [
            InlineKeyboardButton("artikle", callback_data='a22_learn_artikle'),
            InlineKeyboardButton("modal verbs", callback_data='a22_learn_modal'),
            InlineKeyboardButton("⁉️", callback_data='de_learn_preposition'),
        ],
        [
            InlineKeyboardButton("⁉️", callback_data='a22_learn_fragewort'),
            InlineKeyboardButton("verben", callback_data='a22_learn_verbs'),
            InlineKeyboardButton("⁉️", callback_data='reflexive'),
        ],
        [
            InlineKeyboardButton("⁉️", callback_data='de__trotzdem'),
            InlineKeyboardButton("⁉️", callback_data='de_artikle'),
            InlineKeyboardButton("⁉️", callback_data='de_artikle'),
        ],
        # [
        #   InlineKeyboardButton(" AI Chat", callback_data='a22_ai_chat'),  
        # ],
        [
            InlineKeyboardButton("Back", callback_data='Back_main_menu'),
        ]
    ],
    'keyboard_a22_quiz' : [
        [
            InlineKeyboardButton("Artikle 🏁", callback_data='de_artikle'),
            InlineKeyboardButton("Adjectives 🏁", callback_data='de_adjectives'),
            InlineKeyboardButton("preposition 🏁", callback_data='de_preposition'),
        ],
        [
            InlineKeyboardButton("fragewort 🏁", callback_data='a22_quiz_fragewort'),
            InlineKeyboardButton("verben", callback_data='de_quiz_verben'),
            InlineKeyboardButton("reflexiv 🏁", callback_data='de_reflexive'),
        ],
        [
            InlineKeyboardButton("Trotzdem/deshalb", callback_data='de_quiz_trotzdem'),
            InlineKeyboardButton("Modal Verbs", callback_data='a22_quiz_modal_verbs'),
            InlineKeyboardButton("⁉️", callback_data='de_artikle'),
        ],
        [
            InlineKeyboardButton("Back", callback_data='Back_main_menu'),
        ]
    ],
    'a22_story_a' : [
        [
            InlineKeyboardButton("Story 1 🧛", callback_data='story1'),
            InlineKeyboardButton("Story 2 🧛", callback_data='Story2'),
        ],
        [
            InlineKeyboardButton("Back", callback_data='Back_main_menu')
        ]
    ],
    'keyboard_story': [
        [
            InlineKeyboardButton("🔙 ", callback_data='Back_main_menu'),
            InlineKeyboardButton("Next ⏭️", callback_data='StoryB'),
        ]
    ]
}


A1_1_keyboard = [
    [
        InlineKeyboardButton("words", callback_data='A1.1_learn_word'),
        InlineKeyboardButton("verbs", callback_data='A1.1_learn_verb'),
        InlineKeyboardButton("Grammar", callback_data='A1.1_learn_grammar'),
    ],
    [
        InlineKeyboardButton("words ⁉️", callback_data='A1.1_quiz_word'),
        InlineKeyboardButton("verbs ⁉️", callback_data='A1.1_quiz_verb'),
        InlineKeyboardButton("Grammar ⁉️", callback_data='A1.1_quiz_grammar'),
    ]
]

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
    # [
    #     InlineKeyboardButton("EN Word 🤓 ", callback_data='en_word'),
    #     InlineKeyboardButton("News 📰", callback_data='news'),
    #     InlineKeyboardButton("quiz 💯 ", callback_data='en_quiz'),
    # ],
    [
        InlineKeyboardButton("Word 🤓 ", callback_data='de_word'),
        # InlineKeyboardButton("DE News 📰 ", callback_data='de_news'),
        InlineKeyboardButton("quiz 💯 ", callback_data='de_quiz')
    ],
    [
        # InlineKeyboardButton("EN Podcast 🦻", callback_data='en_podcast'),
        InlineKeyboardButton("News 📺", callback_data='de_podcast')
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
    
        # Create the `users` table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT,
            join_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create the `scores` table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
    ''')

    # Create the `quizzes` table (optional)
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")


### add/update score
def add_score(user_id, quiz_name, points):
    # Connect to the database
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Check if the user already has a score entry for the quiz
    c.execute('''
        SELECT score FROM scores
        WHERE user_id = ? AND quiz_name = ?
    ''', (user_id, quiz_name))
    existing_score = c.fetchone()

    if existing_score:
        # Update the score if an entry exists
        new_score = existing_score[0] + points
        c.execute('''
            UPDATE scores
            SET score = ?, attempted_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND quiz_name = ?
        ''', (new_score, user_id, quiz_name))
        print(f"Updated score for user {user_id} in quiz '{quiz_name}' to {new_score} points.")
    else:
        # Insert a new entry if none exists
        c.execute('''
            INSERT INTO scores (user_id, quiz_name, score)
            VALUES (?, ?, ?)
        ''', (user_id, quiz_name, points))
        print(f"Added new score entry for user {user_id} in quiz '{quiz_name}' with {points} points.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    
    
### fetch users score for all his quizes 
def get_user_scores(user_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    # Query to fetch all scores for the user
    c.execute('''
        SELECT quiz_name, score
        FROM scores
        WHERE user_id = ?
    ''', (user_id,))
    
    # Fetch all results
    scores = c.fetchall()

    # Close the connection
    conn.close()

    # Format the scores for display
    if scores:
        result = {quiz: score for quiz, score in scores}
        return result
    else:
        return "No scores found for this user."
    

async def my_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested my score.".format(update.effective_user.first_name))
    user_id = update.effective_user.id
    user_scores = get_user_scores(user_id)
    
    if isinstance(user_scores, dict):
        # Format each quiz score on a new line
        message = "\n".join([f"{quiz}: {score}" for quiz, score in user_scores.items()])
    else:
        # Handle case where no scores are found
        message = user_scores  # This would be the "No scores found" message
    
    # Send the formatted message
    await update.message.reply_text(f"Your Scores:\n{message}")
    
    
### get_dialog 
async def get_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested dialog.".format(update.effective_user.first_name))
    user_text = update.message.text.split(maxsplit=1)[1]
    chatgpt_response = get_dialog(user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=chatgpt_response)
    
# Help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested help.".format(update.effective_user.first_name))
    await update.message.reply_text("I can help you learn 504 essential words daily.\n"
                                    "- /help to get this help message\n"
                                    "- /start to start learning\n"
                                    "- /myscore to see your result and progress\n"
                                    "Your data helps personalize your learning experience.")


# ### handle back button 
# async def previous_button_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("User {} requested previous button.".format(update.effective_user.first_name))
#     reply_markup = InlineKeyboardMarkup(keyboards.get(previous_keyboard.pop()))
#     await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)
    
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
    

def read_german_json_file(file_name, key):
    with open(file_name, "r") as file:
        data = json.load(file)[key]
        word = random.sample(data, 1)[0]
        return word
    
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
    
    
    
### send german auddio to users
async def de_podcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested DE audio.".format(update.effective_user.first_name))
    print(update.message)
    title, videos = fetch_videos_news()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=title)
    await context.bot.send_video(chat_id=update.effective_chat.id, video=videos)
    
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22'))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)
    
    
    
### send a audiofile to users
async def podcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested EN audio.".format(update.effective_user.first_name))
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
    
    
def read_german_nouns(filename: str, count: int):
    with open(filename, "r") as file:
        data = json.load(file)['nouns']
        noun = random.sample(data, count)
        return noun
    
async def de_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_quiz'))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)


### handle todo 
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested todo.".format(update.effective_user.first_name))
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Comming Soon ...")
    
    
    
    
def read_german_reflexive(file_name, key):
    with open(str(file_name), "r") as file:
        reflexes = json.load(file)[str(key)]
        reflex = random.choice(reflexes)
        return reflex
    
    
def read_german_adjectives():
    with open("german_adjectives.json", "r") as file:
        adjectives = json.load(file)['adjectives']
        adj = random.choice(adjectives)
        return adj

# def read_german_a2_modals():
#     with open("german_A2_modals.json", "r") as file:
#         modals = json.load(file)['modals']
#         modal = random.choice(modals)
#         return modal

### handle de_quiz_trotzdem button 
async def de_quiz_trotzdem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for trotzdem.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz for trotzdem.".format(update.effective_user.first_name))
    trotzdem = read_german_json_file('german_A2_trotzdem_quiz.json', 'trotzdem')
    options = random.sample(trotzdem['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=trotzdem['question'],
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(trotzdem['correct_answer']),
                            explanation=f"{trotzdem['explanation']} quiz_type=a22_trotzdem")

    
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(trotzdem['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_trotzdem'
    }
    
### handle modal_verbs quiz
async def a22_quiz_modal_verbs_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for modal verbs.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz for modal verbs.".format(update.effective_user.first_name))
    modal_verbs = read_german_json_file('german_A2_modal_verbs_quiz.json', 'questions')
    options = random.sample(modal_verbs['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id,
                            question=modal_verbs['question'],
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(modal_verbs['correct_answer']),
                            explanation=f"{modal_verbs['explanation']} quiz_type=a22_modal_verbs")
    
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(modal_verbs['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_modal_verbs'  
    }
    
### handle de_quiz_verben button
async def de_quiz_verben(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for verben.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz for verben.".format(update.effective_user.first_name))
    verben = read_german_json_file('german_A2_verbs_quiz.json', 'verb_quiz')
    options = random.sample(verben['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=verben['question'],
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(verben['correct_answer']),
                            explanation=f"{verben['explanation']} quiz_type=a22_verben")
    
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(verben['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_verben'
    }
    
    # reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_quiz'))
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)
async def de_reflexiv_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for reflexiv.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz for reflexiv.".format(update.effective_user.first_name))
    reflex = read_german_json_file('german_reflexiv.json', 'reflexive_verben')
    options = random.sample(reflex['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=reflex['question'],
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(reflex['correct_answer']),
                            explanation=f"{reflex['explanation']} quiz_type=a22_reflexive")

    
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(reflex['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_reflexive'
    }
    
    # reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_quiz'))
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)
    
### read json file 
def read_german_prepositions():
    with open("german_prepositions.json", "r") as file:
        prepositions = json.load(file)['prepositions']
        pre = random.choice(prepositions)
        return pre
    
async def de_preposition_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for prepositions.".format(update.effective_user.first_name))
    logging.info("User {} requested Deutsch quiz for prepositions.".format(update.effective_user.first_name))
    adj = read_german_prepositions("german_A2_modal_verbs_quiz.json", 'questions')
    answer_index = 0
    options = random.sample(adj['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=adj['question'], 
                            options=options,    
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(adj['correct_answer']),
                            explanation=f"{adj['explanation']} quiz_type=a22_prepositions")
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(adj['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_prepositions'
    }
    
### read german_adjectives.json file and prepare the quiz for user
async def dde_adjectives_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("User {} requested Deutsch quiz for adjectives.".format(update.effective_user.first_name))
    adj = read_german_adjectives()
    answer_index = 0 
    options = random.sample(adj['choices'], 4)
    
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=adj['question'], 
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(adj['correct_answer']),
                            explanation=f"{adj['explanation']} quiz_type=a22_adjectives")
    
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(adj['correct_answer']),
        'user_results': {},
        'keyboard_key': 'keyboard_a22_quiz',
        'quiz_type': 'a22_adjectives'
    }
    
### handle back nuttons
async def back_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch back to main menu.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get(user_navigation_stacks[update.effective_user.id].pop()))
    await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)
    
    
### handle button A2.2
async def menu_a22(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22'))

    user_navigation_stacks.setdefault(update.effective_user.id, []).append('main_keyboard')
    
    await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)
    logging.info("User {} requested Deutsch menu A2.2.".format(update.effective_user.first_name))


async def a22_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch story A.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('a22_story_a'))
    user_navigation_stacks.setdefault(update.effective_user.id, []).append('keyboard_a22')
    await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)
    
### read story a
async def a22_story_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch story A.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_story'))
    user_navigation_stacks.setdefault(update.effective_user.id, []).append('a22_story_a')
    story = read_stories_json_file("german_story_A.json", 0)
    await update.callback_query.edit_message_text(f"{story['title']}", reply_markup=reply_markup)
    

async def a22_learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_learn'))
    user_navigation_stacks.setdefault(update.effective_user.id, []).append('keyboard_a22')
    await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)

def read_german_verbs(file_name: str, count: int):
    with open(str(file_name), "r") as file:
        verbs = json.load(file)['verbs']
        verb = random.sample(verbs, count)[0]
        return verb
    
async def a22_ai_chat_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2. ai chat".format(update.effective_user.first_name))
    ### get user prompt and reply by AI
    global user_data
    user = user_data.get(update.effective_user.id, None)
    if not user:
        ### add user into database 
        user_data[update.effective_user.id] = {
            "quota_limit" : 10,
            "used_chats" : 0,
            "conversation_history" : []
        }
    if user_data[update.effective_user.id]['used_chats'] >= user_data[update.effective_user.id]['quota_limit']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have reached your quota limit.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Chat Enabled. Type your message to continue.")
        # user_data[update.effective_user.id]['used_chats'] += 1
        # user_data[update.effective_user.id]['conversation_history'].append({"role": "user", "content": update.message.text})
        # response = get_dialog(update.message.text)
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response} \n limit: {user_data[update.effective_user.id]['quota_limit'] - user_data[update.effective_user.id]['used_chats']}")
            
    
async def a22_learn_modal_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2. learn modal verbs".format(update.effective_user.first_name))
    ### read related file and show the result to user 
    modal = read_german_json_file("german_A2_modal_verbs.json", 'modal_verbs')
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_learn'))
    conjugation_modal_present = "🙌🙌🙌🙌\n-----Present-----\n"+"\n".join(modal['conjugation']['present'])
    conjugation_modal_past = "🥂🥂🥂🥂\n-----Past-----\n"+"\n".join(modal['conjugation']['past'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{modal['verb']} - {modal['definition']} {modal['emoji']} \n{conjugation_modal_present}\n{conjugation_modal_past} \nExamples:\n🫰{modal['examples'][0]}\n🫰{modal['examples'][1]}\n🫰{modal['examples'][2]}")
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Select an option:", reply_markup=reply_markup)

### handle a22 learn verbs
async def a22_learn_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2. learn verb".format(update.effective_user.first_name))
    ### read related file and show the result to user 
    verb = read_german_verbs('german_A2_verbs_learn.json', 1)
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_learn'))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{verb['verb']} - {verb['definition']} {verb['emoji']} \nExamples:\n🫰{verb['examples'][0]}\n🫰{verb['examples'][1]}\n🫰{verb['examples'][2]}")
    await context.bot.send_message(chat_id=update.effective_chat.id,text="Select an option:", reply_markup=reply_markup)
        
        
### handle a22_quiz menu
async def a22_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2.".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_quiz'))
    user_navigation_stacks.setdefault(update.effective_user.id, []).append('keyboard_a22') # Milad

    await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)


### get stories title
def read_stories_json_file(file_name, index):
    with open(file_name, "r") as file:
        data = json.load(file)['stories'][index]
        
        # Extract titles of all stories
        # titles = [story['title'] for story in data['stories']]
        
        return data

    

### handle a22_quiz_fragewort menu
async def a22_quiz_fragewort(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch quiz for fragewort A2.2.".format(update.effective_user.first_name))
    ### read from german_fragewort.json
    fragewort = read_german_json_file('german_fragewort.json', 'questions')
    options = random.sample(fragewort['choices'], 4)
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=fragewort['question'], 
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=options.index(fragewort['correct_answer']),
                            explanation=fragewort['explanation'],
                            )
     # Store poll data
     ### serialize keyboard
    active_polls[poll_message.poll.id] = {
        'correct_option_id': options.index(fragewort['correct_answer']),
        'user_results': {},
        'keyboard_key': "keyboard_a22_quiz"  # Store a reference to the keyboard
    }
    # reply_markup = InlineKeyboardMarkup(keyboard_a22_quiz)
    # await update.callback_query.edit_message_text("Select an option:", reply_markup=reply_markup)   
    
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        poll_id = update.poll_answer.poll_id
        user_id = update.poll_answer.user.id
        selected_option = update.poll_answer.option_ids[0]
        correct_option_id = active_polls[poll_id]['correct_option_id']
        quiz_type = active_polls[poll_id]['quiz_type']
        if selected_option == correct_option_id:
            active_polls[poll_id]['user_results'][user_id] = True
            print("User {} selected the correct option.".format(user_id))
            add_score(user_id, str(quiz_type), 5)
            active_polls[poll_id]['quiz_type'] = None
        else:
            active_polls[poll_id]['user_results'][user_id] = False
            add_score(user_id, str(quiz_type), -3)
            active_polls[poll_id]['quiz_type'] = None
            print("User {} selected the wrong option.".format(user_id))
            
        # Later, retrieve the keyboard using the identifier
        keyboard_key = active_polls[poll_id]['keyboard_key']
        
        reply_markup = InlineKeyboardMarkup(keyboards.get(keyboard_key))
        await context.bot.send_message(chat_id=update.poll_answer.user.id, text="Select an option:", reply_markup=reply_markup)
    except Exception as e:
        print(f"An error occurred: {e}")
         
### return back to main menu 
# async def de_back_quiz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("User {} requested Deutsch back to main menu.".format(update.effective_user.first_name))
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     user_navigation_stacks.setdefault(update.effective_user.id, []).append('keyboard_a22')
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)

artikle_color = {
    'der': '🔵',
    'die': '🔴',
    'das': '🟢' 
}
async def a22_learn_artikles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch menu A2.2 learn artikles".format(update.effective_user.first_name))
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_learn'))
    noun = read_german_nouns('german_a22_nouns.json', 1)[0]
    color = artikle_color.get(noun.get('artikel'), ' ')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Artikel: {color} {noun['artikel']} {noun['noun']}\nDefinition: {noun['definition']} {noun['emoji']}\nExample: {noun['examples'][0]}", reply_markup=reply_markup)
    
async def de_artikle_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested German quiz.".format(update.effective_user.first_name))
    options = ['der', 'die', 'das']
    word = read_german_nouns('german_a22_nouns.json', 1)[0]
    answer_index = 0 
    if word['artikel'] == 'der':
        answer_index = 0
    elif word['artikel'] == 'die':
        answer_index = 1
    elif word['artikel'] == 'das':
        answer_index = 2
    poll_message = await context.bot.send_poll(chat_id=update.effective_chat.id, 
                            question=word['noun'], 
                            options=options,
                            is_anonymous=False, type='quiz',
                            correct_option_id=answer_index,
                            explanation=word['definition'])
    
        ### serialize keyboard
    active_polls[poll_message.poll.id] = {
        'correct_option_id': answer_index,
        'user_results': {},
        'keyboard_key': "keyboard_a22_quiz",  # Store a reference to the keyboard
        'quiz_type': 'a22_artikle'
    }
    # reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22_quiz'))
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option:", reply_markup=reply_markup)
    
    
### send a quiz/poll to user from the words
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested quiz.".format(update.effective_user.first_name))
    
    ### get a word
    # question_list = get_three_words()
    # correct_word  = random.choice(question_list)
    # correct_option_id = question_list.index(correct_word)
    # await context.bot.send_poll(chat_id=update.effective_chat.id, 
    #                             question=correct_word['word'], 
    #                             options=[x['definition'] for x in question_list ],
    #                             is_anonymous=False, type='quiz',
    #                             correct_option_id=question_list.index(correct_word),
    #                             explanation=correct_word['examples'][0])
    
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
    reply_markup = InlineKeyboardMarkup(keyboards.get('main_keyboard'))
    # user_navigation_stacks[update.effective_user.id] = ['main_keyboard']
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
    global user_data
    user_id = update.effective_user.id
    message = update.message['text']
    user = user_data.get(user_id, None)
    if not user:
        ### add user into database
        response = "AI Chat is not enabled for you."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response )
        return
    if user_data[user_id]['used_chats'] >= user_data[user_id]['quota_limit']:
        response = "You have reached your quota limit."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response )
        return
    else:
        user_data[user_id]['used_chats'] += 1
        response = get_dialog(message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{response} \n limit: {user_data[user_id]['quota_limit'] - user_data[user_id]['used_chats']}" )
    
        
    # Store message interaction
    # conn = sqlite3.connect('user_data.db')
    # c = conn.cursor()
    
    # try:
    #     # Store message
    #     c.execute('''INSERT INTO user_interactions 
    #                 (user_id, message_id, message_type, message_content, timestamp)
    #                 VALUES (?, ?, ?, ?, ?)''',
    #             (user.id, message.message_id, 
    #             message.content_type, message.text, 
    #             datetime.now().isoformat()))
    #     # Update last active timestamp
    #     c.execute('''UPDATE users 
    #                 SET last_active = ? 
    #                 WHERE user_id = ?''',
    #             (datetime.now().isoformat(), user.id))
    # except AttributeError:
    #     print("Message is not text.")
    
    # conn.commit()
    # conn.close()
    
    # print("User {} requested help.".format(update.effective_user.first_name))
    # await update.message.reply_text("I can help you learn Deutsch :) .\n"
    #                                 "- /help to get this help message\n"
    #                                 "- /start to start learning\n"
    #                                 "Your data helps personalize your learning experience.")



async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} donated.".format(update.effective_user.first_name))
    donation_text = "Thanks for your donation!\n\n https://paypal.me/millad90s?country.x=DE&locale.x=en_US"
        
    await update.callback_query.edit_message_text(donation_text)
    


def get_de_word():
    # Load words from JSON
    with open("german_nouns.json", "r") as file:
        words_data = json.load(file)
        index=random.choice(list(words_data))
        word = words_data.get(index)
        return random.sample(word, 1)[0]
    
    
### get german word 
async def de_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested a DE WORD.".format(update.effective_user.first_name))
    word  = get_de_word()
    
    chat_id = update.effective_chat.id
    await update.callback_query.edit_message_text(f"------> {word['artikel']} {word['noun']} <----\nTranslation: {word['translation']}☝️\n\nExamples:\n1️⃣ {word['examples'][0]} \n2️⃣ {word['examples'][1]} \n  🚥🚥🚥🚥🚥🚥")
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{word['artikel']} {word['noun']}\nTranslation: {word['translation']}\n\nExamples:\n1️⃣ {word['examples'][0]} \n2️⃣ {word['examples'][1]}")
    await context.bot.send_message(
        chat_id=chat_id,
        text="Select an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )        
async def start_learning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} started learning.".format(update.effective_user.first_name))
    
    word  = get_a_word()[0]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Word: {word['word']}\nDefinition: {word['definition']}\nPhonetic: {word['phonetic']}\n\nExamples:\n1️⃣: {word['examples'][0]} \n2️⃣ {word['examples'][1]} " + f"\n\n🗻🗻🗻🗻🗻")
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
    
### get deutsch news
async def get_news_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested Deutsch news.".format(update.effective_user.first_name))
    news = random.sample(read_news(count=10), 1)[0]
    await update.callback_query.edit_message_text(news['description'] +'\n\n'+ news['learning_text'])
    chat_id = update.effective_chat.id
    # Send the menu again
    reply_markup = InlineKeyboardMarkup(keyboards.get('keyboard_a22'))
    await context.bot.send_message(
        chat_id=chat_id,
        text="Select an option:",
        reply_markup=reply_markup
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
    logging.debug("Starting bot...")
    
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
    application.add_handler(CommandHandler("myscore", my_score))
    application.add_handler(CommandHandler("todo", todo))
    application.add_handler(CommandHandler("get_dialog", get_reply))
    # application.add_handler(CommandHandler("word", word))
    application.add_handler(CommandHandler("admin_send_all", admin_sen_allow))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))
    # application.add_handler(CallbackQueryHandler(show_user_data, pattern='^view_data$'))
    # application.add_handler(CallbackQueryHandler(start_learning, pattern='^en_word$'))
    application.add_handler(CallbackQueryHandler(de_word, pattern='^de_word$'))
    application.add_handler(CallbackQueryHandler(donate, pattern='^donate$'))
    # application.add_handler(CallbackQueryHandler(daily_review, pattern='^daily_review$'))
    application.add_handler(CallbackQueryHandler(get_news, pattern='^news$'))
    application.add_handler(CallbackQueryHandler(get_news_de, pattern='^A2.2_news$'))
    # application.add_handler(CallbackQueryHandler(settings, pattern='^setting$'))
    # application.add_handler(CallbackQueryHandler(podcast, pattern='^en_podcast$'))
    application.add_handler(CallbackQueryHandler(de_podcast, pattern='^A2.2_podcast$'))
    # application.add_handler(CallbackQueryHandler(quiz, pattern='^en_quiz$'))
    # application.add_handler(CallbackQueryHandler(grammar, pattern='^grammar$'))
    # application.add_handler(CallbackQueryHandler(grammar_quiz, pattern='^grammar_quiz$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_quiz$'))
    
    #### de_quiz_artikle
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_artikle$'))
    application.add_handler(CallbackQueryHandler(dde_adjectives_quiz, pattern='^de_adjectives$'))
    application.add_handler(CallbackQueryHandler(de_preposition_quiz, pattern='^de_preposition$'))
    application.add_handler(CallbackQueryHandler(de_reflexiv_quiz, pattern='^de_reflexive$'))
    application.add_handler(CallbackQueryHandler(de_quiz_verben, pattern='^de_quiz_verben$'))
    application.add_handler(CallbackQueryHandler(a22_quiz_modal_verbs_func, pattern='^a22_quiz_modal_verbs$'))
    application.add_handler(CallbackQueryHandler(de_quiz_trotzdem, pattern='^de_quiz_trotzdem$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_datdat$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_datdat_dat$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_datdat_akk$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_datdat_dat_akk$'))
    application.add_handler(CallbackQueryHandler(de_artikle_quiz, pattern='^de_datdat_dat_akk_dat$'))    
    # application.add_handler(CallbackQueryHandler(de_back_quiz_menu, pattern='^Back_quiz_menu$'))
    
    ### back_buttons
    application.add_handler(CallbackQueryHandler(back_main_menu, pattern='^Back_main_menu$'))
    ### A2.2
    
    ### A2.2 Learn
    application.add_handler(CallbackQueryHandler(a22_learn , pattern='^A2.2_learn$'))
    application.add_handler(CallbackQueryHandler(a22_learn_artikles, pattern='^a22_learn_artikle$'))
    application.add_handler(CallbackQueryHandler(a22_learn_verbs, pattern='^a22_learn_verbs$'))
    application.add_handler(CallbackQueryHandler(a22_learn_modal_func, pattern='^a22_learn_modal$'))
    application.add_handler(CallbackQueryHandler(a22_ai_chat_func, pattern='^a22_ai_chat$'))
    
    ### A2.2 Quiz
    application.add_handler(CallbackQueryHandler(menu_a22, pattern='^A2.2$'))
    application.add_handler(CallbackQueryHandler(a22_quiz, pattern='^A2.2_quiz$'))
    application.add_handler(CallbackQueryHandler(a22_story, pattern='^a22_story$'))
    application.add_handler(CallbackQueryHandler(a22_story_a, pattern='^story1$'))
    application.add_handler(CallbackQueryHandler(a22_quiz_fragewort, pattern='^a22_quiz_fragewort$'))
    application.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()