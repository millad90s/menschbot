import random
import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat
from handlers.admin_commands import start_handler_test
from models.users import User

@pytest.mark.asyncio
async def test_start_command():
    """
    Test the /start command handler.
    """
    # Create a mock Telegram User with actual test data
    user = User(id=random.randint(1, 1000), username="testuser", first_name="Test", last_name="User", language_code="en")
    

    # Mock the Telegram Chat
    chat = Chat(id=2140876637, type="private")

        # Fully mock the Telegram Message
    message = MagicMock()
    message.chat = chat
    message.from_user = user
    message.text = "/start"
    # message.reply_text = AsyncMock()  # Mock the reply_text method

    # Mock the Update object with the mocked Message
    update = MagicMock()
    update.message = message
    update.effective_user = user  # Mock effective_user with realistic test data
    update.effective_chat = MagicMock(id=chat.id)

    
    # Mock the Context object
    context = AsyncMock()
    context.bot.send_message = AsyncMock()  # Mock the send_message method

    
    # Call the handler
    await start_handler_test(update, context)
    
    # Assert that reply_text was called with the correct message
    context.bot.send_message.assert_called_once_with(chat_id=2140876637, text="Welcome! I’m here to help you learn 504 essential words.")

