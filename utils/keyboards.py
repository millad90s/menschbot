from telegram import InlineKeyboardButton

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
        # [
        #     InlineKeyboardButton("Story 🧛", callback_data='a22_story'),
        # ],
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