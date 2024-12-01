from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
from utils.keyboards import keyboards
from utils.db import (
    update_user_activity
)
from utils import ADMIN_IDD
from models.users import User


### test start handler 
async def start_handler_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code
    }

    new_user = User(username=user_data['username'], id=user_data['id'], first_name=user_data['first_name'], last_name=user_data['last_name'], language_code=user_data['language_code'])
    new_user.save()

    try:
        if update_user_activity(user.id, user.username, user.first_name, user.last_name, user.language_code):
            reply_markup = InlineKeyboardMarkup(keyboards.get('main_keyboard'))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I’m here to help you learn 504 essential words.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error updating user activity. Please contact the admin")
    except Exception as e:
        print(e)

### handle start command
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code
    }

    new_user = User(username=user_data['username'], id=user_data['id'], first_name=user_data['first_name'], last_name=user_data['last_name'], language_code=user_data['language_code'])
    new_user.save()

    try:
        if update_user_activity(user.id, user.username, user.first_name, user.last_name, user.language_code):
            reply_markup = InlineKeyboardMarkup(keyboards.get('main_keyboard'))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I’m here to help you learn 504 essential words.", reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error updating user activity. Please contact the admin")
    except Exception as e:
        print(e)
        
        
### handle help command 
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User {} requested help.".format(update.effective_user.first_name))
    await update.message.reply_text("I can help you learn Deutsch easily and efficiently.\n"
                                    "- /help to get this help message\n"
                                    "- /start to start learning\n"
                                    "- /myscore to see your result and progress\n"
                                    "Your data helps personalize your learning experience.")

async def admin_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_IDD:
        await update.message.reply_text("You are not allowed to use this command.")
    else:
        print("User {} requested help.".format(update.effective_user.first_name))
        users = User.fetch_all_users()
        for user in users:
            user_display = next((attr for attr in [user.first_name, user.last_name, user.username] if attr), "Unknown User")
            try:
                await context.bot.send_message(chat_id=user.id, text=f"""Dear user {user_display} , This is a Broadcast message:\n\n{update.message.text.split(maxsplit=1)[1]}""") #    update.message.text)
            except Exception as e:
                print(f"Error sending message to user {user_display}: {e}")
                
### handle admin_list_users
async def admin_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("User Admin {} requested to view data.".format(update.effective_user.first_name))
    try:
        print("User Admin {} requested to view data.".format(update.effective_user.first_name))
        if str(update.effective_user.id) in ADMIN_IDD:
            users = fetch_all_users()
            num_users = len(users)
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Number of users: {num_users}\n users: {users}")
        else:
            await update.message.reply_text("You are not allowed to use this command.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
### handlers/user_scores handler

            
        