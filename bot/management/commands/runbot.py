import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)
from bot.handlers.base import (
    start,
    language_callback,
    contact_handler,
    handle_name,
    handle_lastname,
    gender_callback,
    handle_birthday,
    handle_location,
    show_about,
    show_vacancies,
    show_feedback_menu,
    handle_feedback,
    save_feedback,
    show_profile,
    change_language,
)
from bot.texts import TEXTS

# Define conversation states
(
    LANGUAGE,
    CONTACT,
    NAME,
    LASTNAME,
    GENDER,
    BIRTHDAY,
    LOCATION,
    MAIN_MENU,
    FEEDBACK_MENU,
    AWAITING_FEEDBACK,
) = range(10)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Get text dictionaries for button matching
        uz_dict = TEXTS['uz']
        ru_dict = TEXTS['ru']

        # Registration conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                LANGUAGE: [
                    CallbackQueryHandler(language_callback, pattern='^lang_')
                ],
                CONTACT: [
                    MessageHandler(filters.CONTACT, contact_handler),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text(TEXTS[c.user_data.get('language', 'uz')]['contact_required']))
                ],
                NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)
                ],
                LASTNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_lastname)
                ],
                GENDER: [
                    CallbackQueryHandler(gender_callback, pattern='^gender_')
                ],
                BIRTHDAY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_birthday)
                ],
                LOCATION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location)
                ],
                MAIN_MENU: [
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['about']}|{ru_dict['about']})$"),
                        show_about
                    ),
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['vacancies']}|{ru_dict['vacancies']})$"),
                        show_vacancies
                    ),
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['feedback']}|{ru_dict['feedback']})$"),
                        show_feedback_menu
                    ),
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['profile']}|{ru_dict['profile']})$"),
                        show_profile
                    ),
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['change_language']}|{ru_dict['change_language']})$"),
                        change_language
                    ),
                ],
                FEEDBACK_MENU: [
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['complaint']}|{ru_dict['complaint']}|{uz_dict['suggestion']}|{ru_dict['suggestion']})$"),
                        handle_feedback
                    ),
                    MessageHandler(
                        filters.Regex(f"^({uz_dict['back']}|{ru_dict['back']})$"),
                        handle_feedback
                    ),
                ],
                AWAITING_FEEDBACK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback)
                ],
            },
            fallbacks=[
                CommandHandler('start', start),
                MessageHandler(filters.COMMAND, start),
            ],
            allow_reentry=True,
            name="main_conversation",
        )

        # Add handlers
        application.add_handler(conv_handler)

        # Start the bot
        self.stdout.write(self.style.SUCCESS('Bot is running...'))
        application.run_polling() 