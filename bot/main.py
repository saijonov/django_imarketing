from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from .handlers.base import (
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
    handle_profile_edit,
    handle_edit_field,
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
    EDIT_PROFILE,
    EDIT_NAME,
    EDIT_LASTNAME,
    EDIT_PHONE,
    EDIT_LOCATION,
)
from .texts import TEXTS
import os
import logging

def create_application():
    """Create and configure the application."""
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Get text dictionaries for button matching
    uz_texts = TEXTS['uz']
    ru_texts = TEXTS['ru']

    # Create conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                CallbackQueryHandler(language_callback, pattern='^lang_'),
            ],
            CONTACT: [
                MessageHandler(filters.CONTACT, contact_handler),
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name),
            ],
            LASTNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_lastname),
            ],
            GENDER: [
                CallbackQueryHandler(gender_callback, pattern='^gender_'),
            ],
            BIRTHDAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_birthday),
            ],
            LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location),
            ],
            MAIN_MENU: [
                MessageHandler(filters.Regex('^🏢 .*marketing.*$'), show_about),
                MessageHandler(filters.Regex('^📋 .*akans.*$'), show_vacancies),
                MessageHandler(filters.Regex('^✉️ .*uroj.*$'), show_feedback_menu),
                MessageHandler(filters.Regex('^👤 .*rofil.*$'), show_profile),
                MessageHandler(filters.Regex('^🌐 .*il.*$'), change_language),
            ],
            FEEDBACK_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback),
            ],
            AWAITING_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_feedback),
            ],
            EDIT_PROFILE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_profile_edit),
            ],
            EDIT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_field),
            ],
            EDIT_LASTNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_field),
            ],
            EDIT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_field),
            ],
            EDIT_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_field),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        name="main_conversation",
        persistent=True,
        allow_reentry=True,
    )

    # Add conversation handler
    application.add_handler(conv_handler)

    return application 