from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import urllib.parse

# Define site URL directly
SITE_URL = 'http://192.168.1.19:8000'

def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_contact_keyboard(text_dict):
    keyboard = [[KeyboardButton(text_dict['share_contact'], request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_gender_keyboard(text_dict):
    keyboard = [
        [
            InlineKeyboardButton(text_dict['male'], callback_data="gender_male"),
            InlineKeyboardButton(text_dict['female'], callback_data="gender_female")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(text_dict):
    keyboard = [
        [text_dict['about'], text_dict['vacancies']],
        [text_dict['feedback'], text_dict['profile']],
        [text_dict['change_language']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_feedback_keyboard(text_dict):
    keyboard = [
        [text_dict['complaint'], text_dict['suggestion']],
        [text_dict['contact']],
        [text_dict['back']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_profile_edit_keyboard(text_dict):
    """Create keyboard for profile editing with exact button text"""
    keyboard = [
        [text_dict['edit_name'], text_dict['edit_lastname']],
        [text_dict['edit_phone'], text_dict['edit_location']],
        [text_dict['back']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_vacancy_details_button(vacancy_id, text_dict, user_data=None):
    """Create button for vacancy details with user data in URL"""
    base_url = f"{SITE_URL}/vacancy/{vacancy_id}"
    
    if user_data:
        # Clean and prepare user data
        clean_data = {
            'name': user_data.get('name', '').strip(),
            'lastname': user_data.get('lastname', '').strip(),
            'phone': user_data.get('phone', '').strip(),
            'location': user_data.get('location', '').strip(),
            'tg_id': str(user_data.get('tg_id', '')),
            'lang': user_data.get('language', 'uz')
        }
        # Only include non-empty values
        params = {k: v for k, v in clean_data.items() if v}
        if params:
            url = f"{base_url}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
        else:
            url = base_url
    else:
        url = base_url

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text_dict['details_button'], url=url)]
    ]) 